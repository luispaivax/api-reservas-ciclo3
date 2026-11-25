"""Cria o usuario administrador inicial.

Uso (na raiz do projeto, com o ambiente virtual ativo):
    alembic upgrade head
    python -m app.seed_admin

As credenciais vem do arquivo .env (que nao vai para o GitHub):
    ADMIN_NOME=...
    ADMIN_EMAIL=...
    ADMIN_SENHA=...

O procedimento e idempotente: pode ser executado varias vezes
sem criar administradores duplicados.
"""

import os
import re
import sys

from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Usuario
from app.security import gerar_hash_senha

TAMANHO_MINIMO_SENHA = 8

# Formato basico: algo@algo.algo, sem espacos e com um unico "@".
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _buscar_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()


def _conferir_existente(usuario: Usuario) -> str:
    """Decide o que fazer quando o e-mail ja esta cadastrado."""
    if not usuario.admin:
        raise ValueError(
            "Ja existe um usuario comum com esse e-mail. "
            "Ele nao foi promovido automaticamente."
        )
    if not usuario.ativo:
        raise ValueError(
            "O administrador existe, mas esta desativado. "
            "Ele nao foi reativado automaticamente."
        )
    return "existente"


def criar_admin_inicial(db: Session, nome: str, email: str, senha: str) -> str:
    """Cria o administrador se ele ainda nao existir.

    Retorna "criado" ou "existente". Lanca ValueError para dados invalidos
    ou quando o e-mail pertence a um usuario comum ou a um admin desativado.
    """
    nome = (nome or "").strip()
    email = (email or "").strip().lower()
    senha = senha or ""

    if not nome or not email or not senha.strip():
        raise ValueError("Defina ADMIN_NOME, ADMIN_EMAIL e ADMIN_SENHA no .env.")
    if not EMAIL_REGEX.match(email):
        raise ValueError("ADMIN_EMAIL invalido.")
    if len(senha) < TAMANHO_MINIMO_SENHA:
        raise ValueError(
            f"ADMIN_SENHA deve ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres."
        )

    # Prevencao de duplicidade: procura pelo e-mail antes de inserir.
    existente = _buscar_por_email(db, email)
    if existente:
        return _conferir_existente(existente)

    admin = Usuario(
        nome=nome,
        email=email,
        senha_hash=gerar_hash_senha(senha),
        admin=True,
        ativo=True,
    )
    db.add(admin)
    try:
        db.commit()
    except IntegrityError:
        # Segunda barreira: a coluna email e UNIQUE no banco.
        # Outro processo pode ter gravado o e-mail entre a busca e o commit.
        db.rollback()
        existente = _buscar_por_email(db, email)
        if existente is None:
            raise  # erro de integridade com outra causa: nao esconder
        return _conferir_existente(existente)
    return "criado"


def main() -> int:
    load_dotenv()
    db = SessionLocal()
    try:
        resultado = criar_admin_inicial(
            db,
            os.getenv("ADMIN_NOME", ""),
            os.getenv("ADMIN_EMAIL", ""),
            os.getenv("ADMIN_SENHA", ""),
        )
    except ValueError as erro:
        print(f"Erro: {erro}")
        return 1
    except OperationalError:
        print("Erro: tabelas nao encontradas. Rode 'alembic upgrade head' antes.")
        return 1
    finally:
        db.close()

    # A senha nunca e exibida.
    if resultado == "criado":
        print("Administrador inicial criado com sucesso.")
    else:
        print("Administrador ja existe. Nenhum registro foi duplicado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
