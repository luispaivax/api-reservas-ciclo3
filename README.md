# API de Reservas de Salas e Laboratórios

API REST desenvolvida utilizando Python, FastAPI, SQLAlchemy, SQLite e Alembic.

## 1. Pré-requisitos

- Python instalado.
- Git instalado.
- Terminal aberto na raiz do projeto.

## 2. Configuração do ambiente virtual

Criar o ambiente virtual:

```bash
python -m venv .venv
```

Ativar no Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Ativar no Linux ou macOS:

```bash
source .venv/bin/activate
```

## 3. Instalação das dependências

```bash
python -m pip install -r requirements.txt
```

Caso o requirements.txt ainda não tenha sido criado, o responsável pela configuração inicial deverá executar:

```bash
python -m pip install fastapi "uvicorn[standard]" sqlalchemy alembic python-dotenv
pip freeze > requirements.txt
```

## 4. Configuração do banco de dados

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```ini
DATABASE_URL=sqlite:///./reservas.db
```

## 5. Migrations com Alembic

### 5.1. Aplicar as migrations existentes

Após clonar o repositório, execute:

```bash
alembic upgrade head
```

Esse comando cria ou atualiza o banco de dados local conforme as migrations do projeto.

### 5.2. Criar uma nova migration

Sempre que houver alterações nos modelos em `app/models.py`, execute:

```bash
alembic revision --autogenerate -m "Descricao da alteracao"
```

Revise o arquivo gerado em `alembic/versions/` e aplique a migration:

```bash
alembic upgrade head
```

### 5.3. Comandos úteis

| Comando | Descrição |
| --- | --- |
| `alembic current` | Exibe a revisão atual do banco. |
| `alembic history` | Exibe o histórico de migrations. |
| `alembic heads` | Exibe as revisões mais recentes. |
| `alembic upgrade head` | Atualiza o banco para a última revisão. |
| `alembic downgrade -1` | Reverte uma revisão; pode causar perda de dados. |

### 5.4. Inicialização do Alembic (somente na configuração inicial do projeto)

Caso o Alembic ainda não esteja configurado:

```bash
alembic init alembic
```

No arquivo `alembic/env.py`, importe os modelos e configure os metadados e a URL do banco:

```python
from app.database import Base, DATABASE_URL
from app import models
```

Substitua `target_metadata = None` por:

```python
config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata
```

Crie e aplique a primeira migration:

```bash
alembic revision --autogenerate -m "Criacao das tabelas iniciais"
alembic upgrade head
```

Não execute `alembic init alembic` novamente se a configuração já estiver no repositório.

## 6. Executar a API

Quando o arquivo `app/main.py` estiver implementado:

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

## 7. Boas práticas para o grupo

- Versionar os modelos, migrations, `alembic.ini` e `requirements.txt` no Git.
- Não versionar o ambiente virtual, o banco local ou o arquivo `.env`.
- Executar `alembic upgrade head` após receber novas migrations.
- Não gerar migrations duplicadas para alterações já versionadas.

Adicione ao `.gitignore`:

```gitignore
.venv/
.env
*.db
__pycache__/
```

Para desativar o ambiente virtual:

```bash
deactivate
```
