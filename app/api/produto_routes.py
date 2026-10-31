
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Produto, Usuario, Auditoria
from app.schemas import ProdutoCriar, ProdutoResposta
from app.auth import exigir_administrador


# ========================================
# CONFIGURAÇÃO DAS ROTAS DE PRODUTOS
# ========================================

router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
)


# ========================================
# MODELO PARA ATIVAR / DESATIVAR PRODUTO
# ========================================

class ProdutoStatusAtualizar(BaseModel):
    ativo: bool


# ========================================
# CADASTRAR PRODUTO
# ========================================

@router.post(
    "/",
    response_model=ProdutoResposta,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_produto(
    dados: ProdutoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    """
    Cadastra um novo produto.
    Apenas administradores podem cadastrar.
    """

    produto_existente = (
        db.query(Produto)
        .filter(Produto.nome == dados.nome)
        .first()
    )

    if produto_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um produto cadastrado com esse nome.",
        )

    produto = Produto(
        nome=dados.nome,
        descricao=dados.descricao,
        preco=dados.preco,
        categoria=dados.categoria,
        ativo=True,
    )

    # Adiciona o produto e obtém seu ID.
    db.add(produto)
    db.flush()

    # Registra a auditoria do cadastro.
    auditoria = Auditoria(
        usuario_id=usuario.id,
        acao="CADASTRO_PRODUTO",
        detalhes=(
            f"Produto cadastrado: "
            f"{produto.nome} (ID: {produto.id})"
        ),
    )

    db.add(auditoria)

    # Salva o produto e a auditoria juntos.
    db.commit()
    db.refresh(produto)

    return produto


# ========================================
# LISTAR PRODUTOS
# ========================================

@router.get(
    "/",
    response_model=list[ProdutoResposta],
)
def listar_produtos(
    db: Session = Depends(get_db),
):
    """
    Lista todos os produtos cadastrados.
    """

    produtos = (
        db.query(Produto)
        .order_by(Produto.id)
        .all()
    )

    return produtos


# ========================================
# EDITAR PRODUTO
# ========================================

@router.put(
    "/{produto_id}",
    response_model=ProdutoResposta,
)
def editar_produto(
    produto_id: int,
    dados: ProdutoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    """
    Atualiza os dados de um produto existente.
    Apenas administradores podem editar.
    """

    # Procura o produto pelo ID.
    produto = (
        db.query(Produto)
        .filter(Produto.id == produto_id)
        .first()
    )

    # Se não existir, retorna erro 404.
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    # Verifica se outro produto já possui o novo nome.
    produto_com_mesmo_nome = (
        db.query(Produto)
        .filter(
            Produto.nome == dados.nome,
            Produto.id != produto_id,
        )
        .first()
    )

    if produto_com_mesmo_nome:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe outro produto cadastrado com esse nome.",
        )

    # Guarda os dados anteriores para a auditoria.
    nome_anterior = produto.nome
    preco_anterior = produto.preco

    # Atualiza os campos do produto.
    produto.nome = dados.nome
    produto.descricao = dados.descricao
    produto.preco = dados.preco
    produto.categoria = dados.categoria

    # Registra quem fez a alteração.
    auditoria = Auditoria(
        usuario_id=usuario.id,
        acao="EDICAO_PRODUTO",
        detalhes=(
            f"Produto editado (ID: {produto.id}). "
            f"Nome anterior: {nome_anterior}. "
            f"Nome atual: {produto.nome}. "
            f"Preço anterior: {preco_anterior}. "
            f"Preço atual: {produto.preco}."
        ),
    )

    db.add(auditoria)

    # Salva as alterações e a auditoria juntas.
    db.commit()
    db.refresh(produto)

    return produto


# ========================================
# ATIVAR / DESATIVAR PRODUTO
# ========================================

@router.patch(
    "/{produto_id}/status",
    response_model=ProdutoResposta,
)
def alterar_status_produto(
    produto_id: int,
    dados: ProdutoStatusAtualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    """
    Ativa ou desativa um produto.

    Apenas administradores podem alterar
    a situação dos produtos.

    O produto não é excluído do banco.
    """

    # Procura o produto pelo ID.
    produto = (
        db.query(Produto)
        .filter(Produto.id == produto_id)
        .first()
    )

    # Produto não encontrado.
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    # Guarda a situação anterior.
    status_anterior = (
        "ATIVO" if produto.ativo else "INATIVO"
    )

    # Verifica se a situação já é a solicitada.
    if produto.ativo == dados.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "O produto já está "
                + ("ativo." if dados.ativo else "inativo.")
            ),
        )

    # Atualiza a situação do produto.
    produto.ativo = dados.ativo

    # Define a nova situação.
    status_novo = (
        "ATIVO" if produto.ativo else "INATIVO"
    )

    # Define a ação da auditoria.
    acao_auditoria = (
        "ATIVACAO_PRODUTO"
        if produto.ativo
        else "DESATIVACAO_PRODUTO"
    )

    # Registra quem realizou a alteração.
    auditoria = Auditoria(
        usuario_id=usuario.id,
        acao=acao_auditoria,
        detalhes=(
            f"Produto: {produto.nome} "
            f"(ID: {produto.id}). "
            f"Situação anterior: {status_anterior}. "
            f"Nova situação: {status_novo}."
        ),
    )

    db.add(auditoria)

    # Salva o produto e a auditoria juntos.
    db.commit()
    db.refresh(produto)

    return produto
