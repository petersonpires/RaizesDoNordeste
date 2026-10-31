import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext


# Carrega as configuracoes do arquivo .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SECRET_KEY nao configurada ou muito curta. "
        "Verifique o arquivo .env."
    )

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def gerar_hash_senha(senha: str) -> str:
    """Gera um hash seguro para a senha."""
    return pwd_context.hash(senha)


def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    """Compara a senha digitada com o hash armazenado."""
    return pwd_context.verify(senha_digitada, senha_hash)


def criar_token(dados: dict) -> str:
    """Cria um token JWT com prazo de validade."""
    dados_token = dados.copy()

    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    dados_token["exp"] = expiracao

    token = jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token


def verificar_token(token: str):
    """Decodifica o token e retorna seus dados, se for valido."""
    try:
        dados = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return dados

    except JWTError:
        return None