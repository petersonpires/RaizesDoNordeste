
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Estoque, Unidade, Produto, Usuario, Auditoria
from app.auth import exigir_administrador


router = APIRouter(
    prefix="/estoque",
    tags=["Estoque"],
)


# Dados necessários para cadastrar um estoque.
class EstoqueCriar(BaseModel):
    unidade_id: int = Field(gt=0)
    produto_id: int = Field(gt=0)
    quantidade: int = Field(ge=0)


# Dados necessários para atualizar a quantidade.
class EstoqueAtualizar(BaseModel):
    quantidade: int = Field(ge=0)


# Formato da resposta da API.
class EstoqueResposta(BaseModel):
    id: int
    unidade_id: int
    produto_id: int
    quantidade: int


@router.post(
    "/",
    response_model=EstoqueResposta,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_estoque(
    dados: EstoqueCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    """Cadastra o estoque de um produto em uma unidade."""

    unidade = (
        db.query(Unidade)
        .filter(Unidade.id == dados.unidade_id)
        .first()
    )

    if not unidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada.",
        )

    produto = (
        db.query(Produto)
        .filter(Produto.id == dados.produto_id)
        .first()
    )

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    estoque_existente = (
        db.query(Estoque)
        .filter(
            Estoque.unidade_id == dados.unidade_id,
            Estoque.produto_id == dados.produto_id,
        )
        .first()
    )

    if estoque_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esse produto já possui estoque cadastrado nessa unidade.",
        )

    estoque = Estoque(
        unidade_id=dados.unidade_id,
        produto_id=dados.produto_id,
        quantidade=dados.quantidade,
    )

    db.add(estoque)
    db.flush()

    auditoria = Auditoria(
        usuario_id=usuario.id,
        acao="CADASTRO_ESTOQUE",
        detalhes=(
            f"Estoque cadastrado para o produto {produto.nome} "
            f"na unidade {unidade.nome}. "
            f"Quantidade: {dados.quantidade}"
        ),
    )

    db.add(auditoria)
    db.commit()
    db.refresh(estoque)

    return estoque


@router.get(
    "/",
    response_model=list[EstoqueResposta],
)
def listar_estoques(
    unidade_id: int | None = None,
    produto_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Lista os estoques, permitindo filtrar por unidade ou produto."""

    consulta = db.query(Estoque)

    if unidade_id is not None:
        consulta = consulta.filter(
            Estoque.unidade_id == unidade_id
        )

    if produto_id is not None:
        consulta = consulta.filter(
            Estoque.produto_id == produto_id
        )

    return consulta.order_by(Estoque.id).all()


@router.put(
    "/{estoque_id}",
    response_model=EstoqueResposta,
)
def atualizar_estoque(
    estoque_id: int,
    dados: EstoqueAtualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    """Atualiza a quantidade disponível de um estoque."""

    estoque = (
        db.query(Estoque)
        .filter(Estoque.id == estoque_id)
        .first()
    )

    if not estoque:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estoque não encontrado.",
        )

    quantidade_anterior = estoque.quantidade
    estoque.quantidade = dados.quantidade

    auditoria = Auditoria(
        usuario_id=usuario.id,
        acao="ATUALIZACAO_ESTOQUE",
        detalhes=(
            f"Estoque ID {estoque.id} atualizado. "
            f"Quantidade anterior: {quantidade_anterior}. "
            f"Nova quantidade: {dados.quantidade}."
        ),
    )

    db.add(auditoria)
    db.commit()
    db.refresh(estoque)

    return estoque
