
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Pedido,
    Pagamento,
    Usuario,
    Unidade,
    Produto,
    ItemPedido,
)
from app.auth import exigir_administrador


router = APIRouter(
    prefix="/relatorios",
    tags=["Relatórios"],
)


# ============================================================
# FUNÇÃO AUXILIAR PARA CALCULAR INDICADORES DE VENDAS
# ============================================================

def calcular_indicadores(db: Session, filtros=None):
    """
    Calcula os indicadores de vendas.
    Pode receber filtros por unidade ou por período.
    """

    if filtros is None:
        filtros = []

    total_pedidos = db.query(
        func.count(Pedido.id)
    ).filter(
        *filtros
    ).scalar() or 0

    pedidos_entregues = db.query(
        func.count(Pedido.id)
    ).filter(
        *filtros,
        Pedido.status == "ENTREGUE"
    ).scalar() or 0

    vendas = db.query(
        Pedido.valor_total
    ).join(
        Pagamento,
        Pagamento.pedido_id == Pedido.id
    ).filter(
        *filtros,
        Pedido.status == "ENTREGUE",
        Pagamento.status == "APROVADO"
    ).all()

    total_vendas = len(vendas)

    faturamento = sum(
        (
            Decimal(str(venda.valor_total))
            for venda in vendas
        ),
        Decimal("0.00")
    )

    ticket_medio = (
        faturamento / total_vendas
        if total_vendas > 0
        else Decimal("0.00")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    return {
        "total_pedidos": total_pedidos,
        "pedidos_entregues": pedidos_entregues,
        "vendas_concluidas": total_vendas,
        "faturamento_total": str(faturamento),
        "ticket_medio": str(ticket_medio),
    }


# ============================================================
# 1. RELATÓRIO GERAL DE VENDAS
# ============================================================

@router.get("/resumo-vendas")
def resumo_vendas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    return calcular_indicadores(db)


# ============================================================
# 2. RELATÓRIO DE VENDAS POR UNIDADE
# ============================================================

@router.get("/vendas-por-unidade/{unidade_id}")
def vendas_por_unidade(
    unidade_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    unidade = db.query(Unidade).filter(
        Unidade.id == unidade_id
    ).first()

    if not unidade:
        raise HTTPException(
            status_code=404,
            detail="Unidade não encontrada."
        )

    indicadores = calcular_indicadores(
        db,
        filtros=[
            Pedido.unidade_id == unidade_id
        ]
    )

    return {
        "unidade_id": unidade.id,
        "unidade_nome": unidade.nome,
        **indicadores,
    }


# ============================================================
# 3. RELATÓRIO DE VENDAS POR PERÍODO
# ============================================================

@router.get("/vendas-por-periodo")
def vendas_por_periodo(
    data_inicio: date = Query(
        ...,
        description="Data inicial no formato AAAA-MM-DD"
    ),
    data_fim: date = Query(
        ...,
        description="Data final no formato AAAA-MM-DD"
    ),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    if data_fim < data_inicio:
        raise HTTPException(
            status_code=400,
            detail="A data final não pode ser anterior à data inicial."
        )

    inicio = datetime.combine(
        data_inicio,
        time.min
    )

    # Limite exclusivo: início do dia seguinte à data final
    fim_exclusivo = datetime.combine(
        data_fim + timedelta(days=1),
        time.min
    )

    indicadores = calcular_indicadores(
        db,
        filtros=[
            Pedido.criado_em >= inicio,
            Pedido.criado_em < fim_exclusivo,
        ]
    )

    return {
        "data_inicio": data_inicio.isoformat(),
        "data_fim": data_fim.isoformat(),
        **indicadores,
    }


# ============================================================
# 4. RELATÓRIO DE PRODUTOS MAIS VENDIDOS
# ============================================================

@router.get("/produtos-mais-vendidos")
def produtos_mais_vendidos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    """
    Lista os produtos mais vendidos.

    Considera somente pedidos ENTREGUES
    com pagamento APROVADO.
    """

    resultados = db.query(
        Produto.id.label("produto_id"),
        Produto.nome.label("produto_nome"),
        func.sum(
            ItemPedido.quantidade
        ).label("quantidade_vendida"),
        func.sum(
            ItemPedido.quantidade * ItemPedido.preco_unitario
        ).label("faturamento_produto"),
    ).join(
        ItemPedido,
        ItemPedido.produto_id == Produto.id
    ).join(
        Pedido,
        Pedido.id == ItemPedido.pedido_id
    ).join(
        Pagamento,
        Pagamento.pedido_id == Pedido.id
    ).filter(
        Pedido.status == "ENTREGUE",
        Pagamento.status == "APROVADO",
    ).group_by(
        Produto.id,
        Produto.nome,
    ).order_by(
        func.sum(ItemPedido.quantidade).desc(),
        Produto.nome.asc(),
    ).all()

    produtos = []

    for resultado in resultados:
        faturamento = Decimal(
            str(resultado.faturamento_produto)
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        produtos.append({
            "produto_id": resultado.produto_id,
            "produto_nome": resultado.produto_nome,
            "quantidade_vendida": int(
                resultado.quantidade_vendida
            ),
            "faturamento_produto": str(faturamento),
        })

    return {
        "total_produtos": len(produtos),
        "produtos": produtos,
    }
