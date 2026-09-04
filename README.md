# Renewal Tracker

API para cadastro e consulta de contratos.

## Requisitos

- Python 3.11 ou superior
- Git

O projeto utiliza FastAPI, SQLAlchemy, Alembic, SQLite e pytest.

## Instalacao no Windows

Clone o repositorio e entre na pasta do projeto:

```powershell
git clone <URL_DO_REPOSITORIO>
cd renovacoes
```

Crie e ative o ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

## Configuracao do banco

Crie o arquivo `.env` a partir do exemplo:

```powershell
copy .env.example .env
```

A configuracao padrao usa SQLite no arquivo `renewal_tracker.db`:

```env
DATABASE_URL="sqlite:///renewal_tracker.db"
```

Aplique as migrations:

```powershell
alembic upgrade head
```

Para conferir a revisao atual:

```powershell
alembic current
```

O resultado esperado e a revisao mais recente identificada como `head`.

## Executando a API

Com o ambiente virtual ativo:

```powershell
uvicorn app.main:app --reload
```

A API ficara disponivel em:

- http://127.0.0.1:8000/
- Documentacao Swagger: http://127.0.0.1:8000/docs

O endpoint de verificacao atual e:

```text
GET /
```

Resposta esperada:

```json
{ "status": "ok" }
```

## Endpoints atuais

Os endpoints de contratos usam o prefixo `/api/v1/contracts`:

```text
GET  /api/v1/contracts/
GET  /api/v1/contracts/{contract_id}
POST /api/v1/contracts/
```

A documentacao Swagger permite testar os endpoints diretamente.

## Executando os testes

```powershell
pytest
```
