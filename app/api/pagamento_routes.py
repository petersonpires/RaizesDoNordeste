from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pagamento, Pedido, Usuario, Auditoria
from app.auth import obter_usuario_atual, exigir_administrador


router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"],
)


METODOS_PERMITIDOS = {
    "PIX",
    "CARTAO_CREDITO",
    "CARTAO_DEBITO",
    "DINHEIRO",
}


class PagamentoCriar(BaseModel):
    pedido_id: int
    metodo: str


class PagamentoResposta(BaseModel):
    id: int
    pedido_id: int
    metodo: str
    status: str
    valor: Decimal


@router.post(
    "/",
    response_model=PagamentoResposta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_pagamento(
    dados: PagamentoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    """Registra um pagamento simulado aprovado ou recusado."""

    metodo = dados.metodo.upper().strip()

    if metodo not in METODOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Método inválido. Use PIX, CARTAO_CREDITO, "
                "CARTAO_DEBITO ou DINHEIRO."
            ),
        )

    pedido = db.query(Pedido).filter(
        Pedido.id == dados.pedido_id
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado.",
        )

    if pedido.usuario_id != usuario.id and usuario.perfil != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para pagar esse pedido.",
        )

    if pedido.status != "CONFIRMADO":
        raise HTTPException(
            status_code=400,
            detail="Somente pedidos confirmados podem receber pagamento.",
        )

    pagamento_existente = db.query(Pagamento).filter(
        Pagamento.pedido_id == pedido.id
    ).first()

    if pagamento_existente:
        raise HTTPException(
            status_code=409,
            detail="Esse pedido já possui um pagamento registrado.",
        )

    # Regra determinística para testes acadêmicos:
    # CARTAO_DEBITO simula recusa da operadora.
    # Os demais métodos simulam aprovação.
    status_pagamento = (
        "RECUSADO" if metodo == "CARTAO_DEBITO" else "APROVADO"
    )

    pagamento = Pagamento(
        pedido_id=pedido.id,
        metodo=metodo,
        status=status_pagamento,
        valor=pedido.valor_total,
    )

    try:
        db.add(pagamento)
        db.flush()

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="PAGAMENTO_SIMULADO",
                detalhes=(
                    f"Pagamento {pagamento.id} {status_pagamento.lower()} "
                    f"para o pedido {pedido.id}. "
                    f"Método: {metodo}. "
                    f"Valor: R$ {pedido.valor_total}."
                ),
            )
        )

        db.commit()
        db.refresh(pagamento)

    except Exception:
        db.rollback()
        raise

    return pagamento


@router.get(
    "/meus",
    response_model=list[PagamentoResposta],
)
def listar_meus_pagamentos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    """Consulta pagamentos dos pedidos do usuário autenticado."""
    return (
        db.query(Pagamento)
        .join(Pedido, Pagamento.pedido_id == Pedido.id)
        .filter(Pedido.usuario_id == usuario.id)
        .order_by(Pagamento.id.desc())
        .all()
    )


@router.get(
    "/",
    response_model=list[PagamentoResposta],
)
def listar_todos_pagamentos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    """Consulta todos os pagamentos. Apenas administradores."""
    return (
        db.query(Pagamento)
        .order_by(Pagamento.id.desc())
        .all()
    )