
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Promocao, Produto, Auditoria, Usuario
from app.auth import exigir_administrador


router = APIRouter(
    prefix="/promocoes",
    tags=["Promoções"],
)


class PromocaoCriar(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    descricao: str | None = None
    produto_id: int = Field(gt=0)
    percentual_desconto: Decimal = Field(gt=0, le=100)
    data_inicio: datetime
    data_fim: datetime
    ativa: bool = True


class PromocaoResposta(BaseModel):
    id: int
    nome: str
    descricao: str | None
    produto_id: int
    percentual_desconto: Decimal
    data_inicio: datetime
    data_fim: datetime
    ativa: bool


class PromocaoEditar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    descricao: str | None = None
    produto_id: int | None = Field(default=None, gt=0)
    percentual_desconto: Decimal | None = Field(
        default=None,
        gt=0,
        le=100,
    )
    data_inicio: datetime | None = None
    data_fim: datetime | None = None



@router.post(
    "/",
    response_model=PromocaoResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_promocao(
    dados: PromocaoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    produto = db.query(Produto).filter(
        Produto.id == dados.produto_id
    ).first()

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado.",
        )

    if dados.data_fim <= dados.data_inicio:
        raise HTTPException(
            status_code=400,
            detail="A data final deve ser posterior à data inicial.",
        )

    promocao = Promocao(
        nome=dados.nome,
        descricao=dados.descricao,
        produto_id=dados.produto_id,
        percentual_desconto=dados.percentual_desconto,
        data_inicio=dados.data_inicio,
        data_fim=dados.data_fim,
        ativa=dados.ativa,
    )

    try:
        db.add(promocao)
        db.flush()

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="CRIACAO_PROMOCAO",
                detalhes=(
                    f"Promoção {promocao.id} criada "
                    f"para o produto {produto.id}, "
                    f"com desconto de "
                    f"{dados.percentual_desconto}%."
                ),
            )
        )

        db.commit()
        db.refresh(promocao)

    except Exception:
        db.rollback()
        raise

    return promocao


@router.get(
    "/",
    response_model=list[PromocaoResposta],
)
def listar_promocoes(
    db: Session = Depends(get_db),
):
    return (
        db.query(Promocao)
        .order_by(Promocao.id.desc())
        .all()
    )


@router.get(
    "/{promocao_id}",
    response_model=PromocaoResposta,
)
def consultar_promocao(
    promocao_id: int,
    db: Session = Depends(get_db),
):
    promocao = db.query(Promocao).filter(
        Promocao.id == promocao_id
    ).first()

    if not promocao:
        raise HTTPException(
            status_code=404,
            detail="Promoção não encontrada.",
        )

    return promocao

@router.patch(
    "/{promocao_id}/desativar",
    response_model=PromocaoResposta,
)
def desativar_promocao(
    promocao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    promocao = db.query(Promocao).filter(
        Promocao.id == promocao_id
    ).first()

    if not promocao:
        raise HTTPException(
            status_code=404,
            detail="Promoção não encontrada.",
        )

    if not promocao.ativa:
        raise HTTPException(
            status_code=400,
            detail="Essa promoção já está desativada.",
        )

    try:
        promocao.ativa = False

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="DESATIVACAO_PROMOCAO",
                detalhes=(
                    f"Promoção {promocao.id} "
                    f"desativada pelo administrador."
                ),
            )
        )

        db.commit()
        db.refresh(promocao)

    except Exception:
        db.rollback()
        raise

    return promocao



@router.patch(
    "/{promocao_id}/reativar",
    response_model=PromocaoResposta,
)
def reativar_promocao(
    promocao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    promocao = db.query(Promocao).filter(
        Promocao.id == promocao_id
    ).first()

    if not promocao:
        raise HTTPException(
            status_code=404,
            detail="Promoção não encontrada.",
        )

    if promocao.ativa:
        raise HTTPException(
            status_code=400,
            detail="Essa promoção já está ativa.",
        )

    try:
        promocao.ativa = True

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="REATIVACAO_PROMOCAO",
                detalhes=(
                    f"Promoção {promocao.id} "
                    f"reativada pelo administrador."
                ),
            )
        )

        db.commit()
        db.refresh(promocao)

    except Exception:
        db.rollback()
        raise

    return promocao



@router.patch(
    "/{promocao_id}/editar",
    response_model=PromocaoResposta,
)
def editar_promocao(
    promocao_id: int,
    dados: PromocaoEditar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_administrador),
):
    promocao = db.query(Promocao).filter(
        Promocao.id == promocao_id
    ).first()

    if not promocao:
        raise HTTPException(
            status_code=404,
            detail="Promoção não encontrada.",
        )

    alteracoes = dados.model_dump(exclude_unset=True)

    if not alteracoes:
        raise HTTPException(
            status_code=400,
            detail="Informe pelo menos um campo para alterar.",
        )

    campos_obrigatorios = {
        "nome",
        "produto_id",
        "percentual_desconto",
        "data_inicio",
        "data_fim",
    }

    for campo in campos_obrigatorios:
        if campo in alteracoes and alteracoes[campo] is None:
            raise HTTPException(
                status_code=400,
                detail=f"O campo {campo} não pode ser nulo.",
            )

    if "produto_id" in alteracoes:
        produto = db.query(Produto).filter(
            Produto.id == alteracoes["produto_id"]
        ).first()

        if not produto:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado.",
            )

    nova_data_inicio = alteracoes.get(
        "data_inicio",
        promocao.data_inicio,
    )
    nova_data_fim = alteracoes.get(
        "data_fim",
        promocao.data_fim,
    )

    if nova_data_fim <= nova_data_inicio:
        raise HTTPException(
            status_code=400,
            detail="A data final deve ser posterior à data inicial.",
        )

    try:
        for campo, valor in alteracoes.items():
            setattr(promocao, campo, valor)

        db.add(
            Auditoria(
                usuario_id=usuario.id,
                acao="EDICAO_PROMOCAO",
                detalhes=(
                    f"Promoção {promocao.id} editada. "
                    f"Campos alterados: "
                    f"{', '.join(alteracoes.keys())}."
                ),
            )
        )

        db.commit()
        db.refresh(promocao)

    except Exception:
        db.rollback()
        raise

    return promocao
