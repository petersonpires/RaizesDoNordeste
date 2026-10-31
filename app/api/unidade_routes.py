
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Unidade, Auditoria
from app.schemas import UnidadeCriar, UnidadeResposta
from app.auth import obter_usuario_atual, exigir_administrador


router = APIRouter(
    prefix="/unidades",
    tags=["Unidades"],
)


@router.post(
    "/",
    response_model=UnidadeResposta,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_unidade(
    dados: UnidadeCriar,
    db: Session = Depends(get_db),
    usuario_atual=Depends(exigir_administrador),
):
    """
    Cadastra uma nova unidade da rede.
    """
    unidade_existente = db.query(Unidade).filter(
        Unidade.nome == dados.nome
    ).first()

    if unidade_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma unidade com esse nome.",
        )

    nova_unidade = Unidade(
        nome=dados.nome,
        endereco=dados.endereco,
        telefone=dados.telefone,
        ativa=True,
    )

    db.add(nova_unidade)
    db.flush()

    registro_auditoria = Auditoria(
        usuario_id=usuario_atual.id,
        acao="CADASTRO_UNIDADE",
        detalhes=f"Unidade cadastrada: {nova_unidade.nome}",
    )

    db.add(registro_auditoria)
    db.commit()
    db.refresh(nova_unidade)

    return nova_unidade


@router.get(
    "/",
    response_model=list[UnidadeResposta],
)
def listar_unidades(
    db: Session = Depends(get_db),
):
    """
    Lista todas as unidades cadastradas.
    """
    unidades = db.query(Unidade).all()

    return unidades
