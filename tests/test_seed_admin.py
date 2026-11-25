"""Testes do administrador inicial.

Executar na raiz do projeto:
    python -m unittest discover -s tests -v

Usa um banco SQLite em memoria, sem tocar no reservas.db.
"""

import io
import os
import unittest
from contextlib import redirect_stdout
from unittest import mock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import seed_admin
from app.database import Base
from app.models import Usuario
from app.security import gerar_hash_senha, verificar_senha
from app.seed_admin import criar_admin_inicial

SENHA = "SenhaForte123"
EMAIL = "admin@teste.com"


class TestAdminInicial(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _inserir(self, admin, ativo):
        self.db.add(Usuario(
            nome="Existente", email=EMAIL,
            senha_hash=gerar_hash_senha(SENHA), admin=admin, ativo=ativo,
        ))
        self.db.commit()

    # --- criacao e senha ---

    def test_cria_admin_ativo(self):
        self.assertEqual(criar_admin_inicial(self.db, "Admin", EMAIL, SENHA), "criado")
        admin = self.db.query(Usuario).one()
        self.assertTrue(admin.admin)
        self.assertTrue(admin.ativo)

    def test_senha_nao_fica_em_texto_puro(self):
        criar_admin_inicial(self.db, "Admin", EMAIL, SENHA)
        admin = self.db.query(Usuario).one()
        self.assertNotIn(SENHA, admin.senha_hash)
        self.assertTrue(admin.senha_hash.startswith("pbkdf2_sha256$"))
        self.assertTrue(verificar_senha(SENHA, admin.senha_hash))
        self.assertFalse(verificar_senha("senha-errada", admin.senha_hash))

    def test_hashes_diferentes_para_mesma_senha(self):
        self.assertNotEqual(gerar_hash_senha(SENHA), gerar_hash_senha(SENHA))

    # --- duplicidade e usuarios existentes ---

    def test_segunda_execucao_nao_duplica(self):
        criar_admin_inicial(self.db, "Admin", EMAIL, SENHA)
        resultado = criar_admin_inicial(self.db, "Admin", " ADMIN@teste.com ", SENHA)
        self.assertEqual(resultado, "existente")
        self.assertEqual(self.db.query(Usuario).count(), 1)

    def test_nao_promove_usuario_comum(self):
        self._inserir(admin=False, ativo=True)
        with self.assertRaises(ValueError):
            criar_admin_inicial(self.db, "Admin", EMAIL, SENHA)
        self.assertFalse(self.db.query(Usuario).one().admin)

    def test_admin_desativado_nao_e_reativado(self):
        self._inserir(admin=True, ativo=False)
        with self.assertRaises(ValueError):
            criar_admin_inicial(self.db, "Admin", EMAIL, SENHA)
        self.assertFalse(self.db.query(Usuario).one().ativo)
        self.assertEqual(self.db.query(Usuario).count(), 1)

    def test_integrity_error_confere_quem_ocupou_o_email(self):
        # Simula a condicao de corrida: a primeira busca nao encontra ninguem,
        # mas um usuario comum ja ocupa o e-mail quando o commit acontece.
        self._inserir(admin=False, ativo=True)
        real = seed_admin._buscar_por_email
        chamadas = []

        def busca_atrasada(db, email):
            chamadas.append(email)
            return None if len(chamadas) == 1 else real(db, email)

        with mock.patch.object(seed_admin, "_buscar_por_email", busca_atrasada):
            with self.assertRaises(ValueError):
                criar_admin_inicial(self.db, "Admin", EMAIL, SENHA)
        self.assertEqual(len(chamadas), 2)
        self.assertEqual(self.db.query(Usuario).count(), 1)

    # --- validacoes ---

    def test_rejeita_emails_invalidos(self):
        for email in ["@", "admin@", "@dominio.com", "a b@c.com", "admin@@x.com", "admin@x"]:
            with self.subTest(email=email):
                with self.assertRaises(ValueError):
                    criar_admin_inicial(self.db, "Admin", email, SENHA)
        self.assertEqual(self.db.query(Usuario).count(), 0)

    def test_aceita_email_valido(self):
        self.assertEqual(
            criar_admin_inicial(self.db, "Admin", "admin.sala@unievangelica.edu.br", SENHA),
            "criado",
        )

    def test_rejeita_senhas_fracas(self):
        for senha in ["", "        ", "curta"]:
            with self.subTest(senha=repr(senha)):
                with self.assertRaises(ValueError):
                    criar_admin_inicial(self.db, "Admin", EMAIL, senha)
        self.assertEqual(self.db.query(Usuario).count(), 0)

    def test_rejeita_nome_vazio(self):
        with self.assertRaises(ValueError):
            criar_admin_inicial(self.db, "   ", EMAIL, SENHA)

    def test_env_example_nao_traz_senha_preenchida(self):
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(raiz, ".env.example"), encoding="utf-8") as arq:
            linhas = [l.strip() for l in arq if l.startswith("ADMIN_SENHA=")]
        self.assertEqual(linhas, ["ADMIN_SENHA="])

    # --- hash malformado ---

    def test_hash_malformado_retorna_false(self):
        for hash_ruim in [
            "", "texto-qualquer", "pbkdf2_sha256$0$AAAA$AAAA",
            "pbkdf2_sha256$-5$AAAA$AAAA", "pbkdf2_sha256$abc$AAAA$AAAA",
            "pbkdf2_sha256$1000$@@@$@@@", "md5$1000$AAAA$AAAA", None,
        ]:
            with self.subTest(hash=hash_ruim):
                self.assertFalse(verificar_senha(SENHA, hash_ruim))


class TestExecucaoPeloTerminal(unittest.TestCase):
    def test_sem_migrations_mostra_mensagem_amigavel(self):
        engine = create_engine("sqlite:///:memory:")  # banco sem tabelas
        sessao = sessionmaker(bind=engine)
        env = {"ADMIN_NOME": "Admin", "ADMIN_EMAIL": EMAIL, "ADMIN_SENHA": SENHA}
        saida = io.StringIO()
        with mock.patch.object(seed_admin, "SessionLocal", sessao), \
                mock.patch.object(seed_admin, "load_dotenv"), \
                mock.patch.dict(os.environ, env), redirect_stdout(saida):
            codigo = seed_admin.main()
        engine.dispose()
        self.assertEqual(codigo, 1)
        self.assertIn("alembic upgrade head", saida.getvalue())
        self.assertNotIn(SENHA, saida.getvalue())


if __name__ == "__main__":
    unittest.main()
