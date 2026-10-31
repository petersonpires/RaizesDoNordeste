from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Nome e localização do banco de dados
DATABASE_URL = "sqlite:///./raizes_do_nordeste.db"

# Criação da conexão com o banco de dados
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Criação das sessões do banco de dados
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base utilizada para criar as tabelas
Base = declarative_base()


# Função que fornece uma sessão do banco de dados
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()