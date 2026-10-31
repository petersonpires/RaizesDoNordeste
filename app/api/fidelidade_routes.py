
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Usuario,
    Pedido,
    Pagamento,
    Fidelidade,
    PontuacaoPedido,
    Auditoria,
)
from app.auth import obter_usuario_atual


router = APIRouter(
    prefix="/fidelidade",
    tags=["Fidelidade"],
)


def buscar_saldo(db: Session, usuario_id: int):
    registros = db.query(Fidelidade).filter(
        Fidelidade.usuario_id == usuario_id
    ).all()

    # Somar registros existentes evita depender de uma
    # restrição UNIQUE ainda não migrada no SQLite.
    return sum(registro.pontos for registro in registros)


@router.post("/aderir")
def aderir_fidelidade(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    if usuario.consentimento_fidelidade:
        raise HTTPException(
            status_code=400,
            detail="Você já participa do programa de fidelidade.",
        )

    try:
        usuario.consentimento_fidelidade = True

        registros = db.query(Fidelidade).filter(
            Fidelidade.usuario_id == usuario.id
        ).all()

        if not registros:
            db.add(
                Fidelidade(
                    usuario_id=usuario.id,
                    pontos=0,
                    atualizado_em=datetime.utcnow(),
                )
            )

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="ADESAO_FIDELIDADE",
                detalhes="Cliente autorizou participação na fidelidade.",
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "mensagem": "Participação na fidelidade ativada.",
        "consentimento_fidelidade": True,
        "pontos": buscar_saldo(db, usuario.id),
    }


@router.post("/sair")
def sair_fidelidade(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    if not usuario.consentimento_fidelidade:
        raise HTTPException(
            status_code=400,
            detail="Você não participa do programa de fidelidade.",
        )

    try:
        usuario.consentimento_fidelidade = False

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="SAIDA_FIDELIDADE",
                detalhes="Cliente desativou participação na fidelidade.",
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "mensagem": "Participação na fidelidade desativada.",
        "consentimento_fidelidade": False,
    }


@router.get("/meus-pontos")
def consultar_meus_pontos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    return {
        "usuario_id": usuario.id,
        "consentimento_fidelidade": usuario.consentimento_fidelidade,
        "pontos": buscar_saldo(db, usuario.id),
    }


@router.post("/pontuar/{pedido_id}")
def pontuar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    if not usuario.consentimento_fidelidade:
        raise HTTPException(
            status_code=400,
            detail="Ative a participação na fidelidade primeiro.",
        )

    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado.",
        )

    if pedido.usuario_id != usuario.id:
        raise HTTPException(
            status_code=403,
            detail="Esse pedido não pertence a você.",
        )

    if pedido.status != "ENTREGUE":
        raise HTTPException(
            status_code=400,
            detail="Somente pedidos entregues podem gerar pontos.",
        )

    pagamento = db.query(Pagamento).filter(
        Pagamento.pedido_id == pedido.id,
        Pagamento.status == "APROVADO",
    ).first()

    if not pagamento:
        raise HTTPException(
            status_code=400,
            detail="O pedido precisa ter pagamento aprovado.",
        )

    pontuacao_existente = db.query(PontuacaoPedido).filter(
        PontuacaoPedido.pedido_id == pedido.id
    ).first()

    if pontuacao_existente:
        raise HTTPException(
            status_code=400,
            detail="Esse pedido já gerou pontos de fidelidade.",
        )

    pontos_ganhos = int(Decimal(str(pedido.valor_total)))

    try:
        # Atualiza o primeiro saldo encontrado.
        # Caso ainda não exista, cria um novo.
        saldo = db.query(Fidelidade).filter(
            Fidelidade.usuario_id == usuario.id
        ).order_by(Fidelidade.id).first()

        if not saldo:
            saldo = Fidelidade(
                usuario_id=usuario.id,
                pontos=0,
            )
            db.add(saldo)

        saldo.pontos += pontos_ganhos
        saldo.atualizado_em = datetime.utcnow()

        db.add(
            PontuacaoPedido(
                pedido_id=pedido.id,
                usuario_id=usuario.id,
                pontos=pontos_ganhos,
            )
        )

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="PONTUACAO_FIDELIDADE",
                detalhes=(
                    f"Pedido {pedido.id} gerou "
                    f"{pontos_ganhos} pontos."
                ),
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "mensagem": "Pontos registrados com sucesso.",
        "pedido_id": pedido.id,
        "pontos_ganhos": pontos_ganhos,
        "saldo_total": buscar_saldo(db, usuario.id),
    }
