"""Funcoes de seguranca para senhas.

A senha nunca e armazenada em texto puro. Usamos PBKDF2-HMAC-SHA256,
da biblioteca padrao do Python (hashlib), com:

- salt aleatorio por senha (16 bytes), para que senhas iguais gerem
  hashes diferentes e tabelas pre-calculadas (rainbow tables) nao funcionem;
- muitas iteracoes, para deixar ataques de forca bruta lentos.

Formato salvo em Usuario.senha_hash:
    pbkdf2_sha256$<iteracoes>$<salt_base64>$<hash_base64>
"""

import base64
import hashlib
import hmac
import secrets

ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000  # valor recomendado pela OWASP para PBKDF2-SHA256
TAMANHO_SALT = 16


def _b64(dados: bytes) -> str:
    return base64.b64encode(dados).decode("ascii")


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash de uma senha para salvar no banco."""
    if not senha:
        raise ValueError("A senha nao pode ser vazia.")

    salt = secrets.token_bytes(TAMANHO_SALT)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, ITERACOES
    )
    return f"{ALGORITMO}${ITERACOES}${_b64(salt)}${_b64(hash_bytes)}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Confere se a senha informada corresponde ao hash salvo.

    Qualquer hash malformado retorna False em vez de lancar excecao.
    """
    try:
        algoritmo, iteracoes, salt_b64, hash_b64 = senha_hash.split("$")
        iteracoes = int(iteracoes)
        if algoritmo != ALGORITMO or iteracoes < 1:
            return False
        salt = base64.b64decode(salt_b64)
        hash_esperado = base64.b64decode(hash_b64)
        hash_calculado = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), salt, iteracoes
        )
    except (ValueError, AttributeError):
        return False

    # compare_digest evita ataques de tempo (timing attacks)
    return hmac.compare_digest(hash_calculado, hash_esperado)
