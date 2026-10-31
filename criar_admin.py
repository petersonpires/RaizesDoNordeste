
from getpass import getpass

from app.database import SessionLocal
from app.models import Usuario
from app.security import gerar_hash_senha


def criar_administrador():
    print("=== Criar administrador ===")

    nome = input("Nome do administrador: ").strip()
    email = input("E-mail do administrador: ").strip().lower()
    senha = getpass("Senha do administrador: ")
    confirmar_senha = getpass("Confirme a senha: ")

    if not nome or not email or not senha:
        print("Erro: todos os campos são obrigatórios.")
        return

    if senha != confirmar_senha:
        print("Erro: as senhas não são iguais.")
        return

    db = SessionLocal()

    try:
        usuario_existente = db.query(Usuario).filter(
            Usuario.email == email
        ).first()

        if usuario_existente:
            print("Já existe um usuário cadastrado com esse e-mail.")
            return

        administrador = Usuario(
            nome=nome,
            email=email,
            senha_hash=gerar_hash_senha(senha),
            perfil="ADMIN",
            ativo=True,
            consentimento_fidelidade=False,
        )

        db.add(administrador)
        db.commit()
        db.refresh(administrador)

        print("\nAdministrador criado com sucesso!")
        print(f"ID: {administrador.id}")
        print(f"E-mail: {administrador.email}")
        print(f"Perfil: {administrador.perfil}")

    except Exception as erro:
        db.rollback()
        print(f"Erro ao criar administrador: {erro}")

    finally:
        db.close()


if __name__ == "__main__":
    criar_administrador()
