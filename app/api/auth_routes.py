from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario, Fidelidade, Auditoria
from app.schemas import UsuarioCriar, UsuarioResposta, TokenResposta
from app.security import gerar_hash_senha, verificar_senha, criar_token
from app.auth import obter_usuario_atual


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
)


@router.post(
    "/registro",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_usuario(
    dados: UsuarioCriar,
    db: Session = Depends(get_db),
):
    """
    Cadastra um novo cliente.
    """

    email = dados.email.lower().strip()

    usuario_existente = db.query(Usuario).filter(
        Usuario.email == email
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail já está cadastrado.",
        )

    novo_usuario = Usuario(
        nome=dados.nome,
        email=email,
        senha_hash=gerar_hash_senha(dados.senha),

        # O cadastro público sempre cria um cliente.
        # Não permitimos que alguém se registre como ADMIN.
        perfil="CLIENTE",

        ativo=True,
        consentimento_fidelidade=dados.consentimento_fidelidade,
    )

    db.add(novo_usuario)
    db.flush()

    if dados.consentimento_fidelidade:
        registro_fidelidade = Fidelidade(
            usuario_id=novo_usuario.id,
            pontos=0,
        )

        db.add(registro_fidelidade)

    registro_auditoria = Auditoria(
        usuario_id=novo_usuario.id,
        acao="CADASTRO_USUARIO",
        detalhes="Novo usuário cadastrado.",
    )

    db.add(registro_auditoria)

    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


@router.post(
    "/login",
    response_model=TokenResposta,
)
def realizar_login(
    formulario: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Verifica as credenciais e gera um token JWT.
    """

    email = formulario.username.lower().strip()

    usuario = db.query(Usuario).filter(
        Usuario.email == email
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    senha_correta = verificar_senha(
        formulario.password,
        usuario.senha_hash,
    )

    if not senha_correta:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este usuário está inativo.",
        )

    token = criar_token(
        {
            "sub": str(usuario.id),
            "perfil": usuario.perfil,
        }
    )

    registro_auditoria = Auditoria(
        usuario_id=usuario.id,
        acao="LOGIN",
        detalhes="Usuário realizou login.",
    )

    db.add(registro_auditoria)
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.get(
    "/me",
    response_model=UsuarioResposta,
)
def consultar_usuario_atual(
    usuario: Usuario = Depends(obter_usuario_atual),
):
    """
    Retorna os dados do usuário autenticado.
    """
    return usuario