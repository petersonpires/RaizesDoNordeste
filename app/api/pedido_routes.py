
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (
    Pedido,
    ItemPedido,
    Produto,
    Estoque,
    Unidade,
    Usuario,
    Auditoria,
    Pagamento,
    Promocao,
)
from app.auth import obter_usuario_atual, exigir_administrador


router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"],
)


CANAIS_PERMITIDOS = {
    "APP",
    "TOTEM",
    "BALCAO",
    "PICKUP",
    "WEB",
}


PROXIMOS_STATUS = {
    "CONFIRMADO": "EM_PREPARO",
    "EM_PREPARO": "PRONTO",
    "PRONTO": "ENTREGUE",
}


class ItemPedidoCriar(BaseModel):
    produto_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class PedidoCriar(BaseModel):
    unidade_id: int = Field(gt=0)
    canal_pedido: str
    observacao: str | None = None
    itens: list[ItemPedidoCriar] = Field(min_length=1)


class ItemPedidoResposta(BaseModel):
    id: int
    produto_id: int
    quantidade: int
    preco_unitario: Decimal


class PedidoResposta(BaseModel):
    id: int
    usuario_id: int
    unidade_id: int
    status: str
    canal_pedido: str
    valor_total: Decimal
    observacao: str | None
    itens: list[ItemPedidoResposta]


# ============================================================
# BUSCAR PEDIDO NO BANCO
# ============================================================

def buscar_pedido_no_banco(db: Session, pedido_id: int):
    return (
        db.query(Pedido)
        .options(joinedload(Pedido.itens))
        .filter(Pedido.id == pedido_id)
        .first()
    )


# ============================================================
# CALCULAR PREÇO COM PROMOÇÃO
# ============================================================

def calcular_preco_com_promocao(
    db: Session,
    produto: Produto,
):
    preco_original = Decimal(str(produto.preco))
    agora = datetime.now()

    promocoes = db.query(Promocao).filter(
        Promocao.produto_id == produto.id,
        Promocao.ativa.is_(True),
        Promocao.data_inicio <= agora,
        Promocao.data_fim >= agora,
    ).all()

    if not promocoes:
        return preco_original

    maior_desconto = max(
        Decimal(str(p.percentual_desconto))
        for p in promocoes
    )

    preco_final = preco_original * (
        Decimal("1") - maior_desconto / Decimal("100")
    )

    return preco_final.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


# ============================================================
# CRIAR PEDIDO
# ============================================================

@router.post(
    "/",
    response_model=PedidoResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_pedido(
    dados: PedidoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    canal = dados.canal_pedido.upper().strip()

    if canal not in CANAIS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Canal inválido. Use APP, TOTEM, "
                "BALCAO, PICKUP ou WEB."
            ),
        )

    unidade = db.query(Unidade).filter(
        Unidade.id == dados.unidade_id
    ).first()

    if not unidade:
        raise HTTPException(
            status_code=404,
            detail="Unidade não encontrada.",
        )

    if not unidade.ativa:
        raise HTTPException(
            status_code=400,
            detail="Essa unidade está inativa.",
        )

    quantidades = {}

    for item in dados.itens:
        quantidades[item.produto_id] = (
            quantidades.get(item.produto_id, 0)
            + item.quantidade
        )

    itens_validados = []
    valor_total = Decimal("0.00")

    for produto_id, quantidade in quantidades.items():
        produto = db.query(Produto).filter(
            Produto.id == produto_id
        ).first()

        if not produto:
            raise HTTPException(
                status_code=404,
                detail=f"Produto {produto_id} não encontrado.",
            )

        if not produto.ativo:
            raise HTTPException(
                status_code=400,
                detail=f"O produto {produto.nome} está inativo.",
            )

        estoque = db.query(Estoque).filter(
            Estoque.unidade_id == dados.unidade_id,
            Estoque.produto_id == produto_id,
        ).first()

        # CORREÇÃO: estoque insuficiente retorna HTTP 409
        if not estoque or estoque.quantidade < quantidade:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Estoque insuficiente para {produto.nome}. "
                    f"Quantidade solicitada: {quantidade}."
                ),
            )

        preco = calcular_preco_com_promocao(db, produto)
        valor_total += preco * quantidade

        itens_validados.append({
            "produto_id": produto_id,
            "quantidade": quantidade,
            "preco_unitario": preco,
        })

    pedido = Pedido(
        usuario_id=usuario.id,
        unidade_id=dados.unidade_id,
        status="CRIADO",
        canal_pedido=canal,
        valor_total=valor_total,
        observacao=dados.observacao,
    )

    try:
        db.add(pedido)
        db.flush()

        for item in itens_validados:
            db.add(
                ItemPedido(
                    pedido_id=pedido.id,
                    produto_id=item["produto_id"],
                    quantidade=item["quantidade"],
                    preco_unitario=item["preco_unitario"],
                )
            )

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="CRIACAO_PEDIDO",
                detalhes=(
                    f"Pedido {pedido.id} criado. "
                    f"Total: R$ {valor_total}."
                ),
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return buscar_pedido_no_banco(db, pedido.id)


# ============================================================
# CONSULTAR MEUS PEDIDOS
# ============================================================

@router.get(
    "/meus",
    response_model=list[PedidoResposta],
)
def listar_meus_pedidos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    return (
        db.query(Pedido)
        .options(joinedload(Pedido.itens))
        .filter(Pedido.usuario_id == usuario.id)
        .order_by(Pedido.id.desc())
        .all()
    )


# ============================================================
# LISTAR PEDIDOS COM FILTRO POR CANAL
# ============================================================

@router.get(
    "/",
    response_model=list[PedidoResposta],
)
def listar_todos_pedidos(
    canalPedido: str | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    consulta = db.query(Pedido).options(
        joinedload(Pedido.itens)
    )

    if canalPedido is not None:
        canal = canalPedido.strip().upper()

        if canal not in CANAIS_PERMITIDOS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Canal inválido. Use APP, TOTEM, "
                    "BALCAO, PICKUP ou WEB."
                ),
            )

        consulta = consulta.filter(
            Pedido.canal_pedido == canal
        )

    return (
        consulta
        .order_by(Pedido.id.desc())
        .all()
    )


# ============================================================
# CONFIRMAR PEDIDO E DESCONTAR ESTOQUE
# ============================================================

@router.post(
    "/{pedido_id}/confirmar",
    response_model=PedidoResposta,
)
def confirmar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    try:
        pedido = buscar_pedido_no_banco(db, pedido_id)

        if not pedido:
            raise HTTPException(
                status_code=404,
                detail="Pedido não encontrado.",
            )

        if pedido.status != "CRIADO":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Não é possível confirmar o pedido. "
                    f"Status atual: {pedido.status}."
                ),
            )

        if not pedido.itens:
            raise HTTPException(
                status_code=400,
                detail="O pedido não possui itens.",
            )

        quantidades = {}

        for item in pedido.itens:
            quantidades[item.produto_id] = (
                quantidades.get(item.produto_id, 0)
                + item.quantidade
            )

        estoques_para_atualizar = []

        for produto_id, quantidade in quantidades.items():
            estoque = db.query(Estoque).filter(
                Estoque.unidade_id == pedido.unidade_id,
                Estoque.produto_id == produto_id,
            ).first()

            # CORREÇÃO: estoque insuficiente retorna HTTP 409
            if not estoque or estoque.quantidade < quantidade:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Estoque insuficiente para confirmar "
                        f"o produto ID {produto_id}."
                    ),
                )

            estoques_para_atualizar.append(
                (estoque, quantidade)
            )

        for estoque, quantidade in estoques_para_atualizar:
            estoque.quantidade -= quantidade

        pedido.status = "CONFIRMADO"

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="CONFIRMACAO_PEDIDO",
                detalhes=(
                    f"Pedido {pedido.id} confirmado. "
                    "Estoque atualizado automaticamente."
                ),
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return buscar_pedido_no_banco(db, pedido_id)


# ============================================================
# CANCELAR PEDIDO
# ============================================================

@router.post(
    "/{pedido_id}/cancelar",
    response_model=PedidoResposta,
)
def cancelar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    try:
        pedido = buscar_pedido_no_banco(db, pedido_id)

        if not pedido:
            raise HTTPException(
                status_code=404,
                detail="Pedido não encontrado.",
            )

        if (
            pedido.usuario_id != usuario.id
            and usuario.perfil != "ADMIN"
        ):
            raise HTTPException(
                status_code=403,
                detail=(
                    "Você não tem permissão para "
                    "cancelar esse pedido."
                ),
            )

        if pedido.status not in {"CRIADO", "CONFIRMADO"}:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Não é possível cancelar o pedido. "
                    f"Status atual: {pedido.status}."
                ),
            )

        pagamento_aprovado = db.query(Pagamento).filter(
            Pagamento.pedido_id == pedido.id,
            Pagamento.status == "APROVADO",
        ).first()

        if pagamento_aprovado:
            raise HTTPException(
                status_code=409,
                detail=(
                    "O pedido possui pagamento aprovado. "
                    "O cancelamento exige um processo "
                    "de estorno, não implementado no mock."
                ),
            )

        status_anterior = pedido.status

        if status_anterior == "CONFIRMADO":
            for item in pedido.itens:
                estoque = db.query(Estoque).filter(
                    Estoque.unidade_id == pedido.unidade_id,
                    Estoque.produto_id == item.produto_id,
                ).first()

                if not estoque:
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "Não foi possível devolver o estoque "
                            f"do produto ID {item.produto_id}."
                        ),
                    )

                estoque.quantidade += item.quantidade

        pedido.status = "CANCELADO"

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="CANCELAMENTO_PEDIDO",
                detalhes=(
                    f"Pedido {pedido.id} cancelado. "
                    f"Status anterior: {status_anterior}."
                ),
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return buscar_pedido_no_banco(db, pedido_id)


# ============================================================
# AVANÇAR STATUS DO PEDIDO
# ============================================================

@router.post(
    "/{pedido_id}/avancar",
    response_model=PedidoResposta,
)
def avancar_status_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    try:
        pedido = buscar_pedido_no_banco(db, pedido_id)

        if not pedido:
            raise HTTPException(
                status_code=404,
                detail="Pedido não encontrado.",
            )

        if pedido.status not in PROXIMOS_STATUS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Não é possível avançar o pedido. "
                    f"Status atual: {pedido.status}."
                ),
            )

        if pedido.status == "CONFIRMADO":
            pagamento = db.query(Pagamento).filter(
                Pagamento.pedido_id == pedido.id,
                Pagamento.status == "APROVADO",
            ).first()

            if not pagamento:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "O pedido precisa ter um pagamento "
                        "aprovado antes de iniciar o preparo."
                    ),
                )

        status_anterior = pedido.status
        novo_status = PROXIMOS_STATUS[status_anterior]

        pedido.status = novo_status

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="ATUALIZACAO_STATUS_PEDIDO",
                detalhes=(
                    f"Pedido {pedido.id}: "
                    f"{status_anterior} -> {novo_status}."
                ),
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return buscar_pedido_no_banco(db, pedido_id)


# ============================================================
# CONSULTAR PEDIDO POR ID
# ============================================================

@router.get(
    "/{pedido_id}",
    response_model=PedidoResposta,
)
def consultar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    pedido = buscar_pedido_no_banco(db, pedido_id)

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado.",
        )

    if (
        pedido.usuario_id != usuario.id
        and usuario.perfil != "ADMIN"
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Você não tem permissão para "
                "consultar esse pedido."
            ),
        )

    return pedido
