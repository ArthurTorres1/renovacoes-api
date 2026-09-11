# Renewal Tracker

API para controlar contratos e acompanhar renovações e vencimentos próximos.

## Visão geral

Esta aplicação expõe uma API REST em FastAPI para:

- cadastrar contratos;
- listar contratos com paginação e filtros;
- consultar contrato por ID;
- atualizar contrato existente;
- excluir contrato;
- gerar resumo de vencimentos por faixa.

A persistência é feita com SQLAlchemy e SQLite, com migrações versionadas pelo Alembic.

## Requisitos

- Python 3.11+
- Git
- Virtualenv / venv

## Estrutura principal

```text
app/
├── api/
│   └── contracts.py
├── core/
│   ├── database.py
│   └── settings.py
├── models/
│   └── contract.py
├── schemas/
│   ├── contract_schema.py
│   └── renewal_summary_schema.py
├── services/
│   └── contract_service.py
├── main.py
migrations/
├── versions/
├── env.py
├── README
alembic.ini
requirements.txt
run.py
tests/
├── conftest.py
├── test_app.py
```

## Configuração do ambiente

Clone o projeto e entre na pasta:

```powershell
git clone <URL_DO_REPOSITORIO>
cd renovacoes-api
```

Crie e ative o ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Crie o arquivo de ambiente a partir do exemplo:

```powershell
copy .env.example .env
```

O exemplo padrão usa SQLite local:

```env
DATABASE_URL="sqlite:///renewal_tracker.db"
```

## Banco de dados e migrations

As migrations já estão prontas e versionadas no projeto. Para aplicar o schema atual no banco local:

```powershell
alembic upgrade head
```

Para verificar a revisão atual:

```powershell
alembic current
```

O banco local gerado pelo projeto é o arquivo `renewal_tracker.db`, e a aplicação foi configurada para trabalhar com ele em ambiente local.

## Executando a API

Com o ambiente virtual ativo, rode:

```powershell
python run.py
```

A API ficará disponível em:

- http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs

### Health check

```http
GET /api/v1/health
```

Resposta esperada:

```json
{
  "status": "ok"
}
```

## Endpoints principais

### Contratos

```http
GET    /api/v1/contracts
GET    /api/v1/contracts/{contract_id}
POST   /api/v1/contracts
PUT    /api/v1/contracts/{contract_id}
DELETE /api/v1/contracts/{contract_id}
```

### Resumo de renovações

```http
GET /api/v1/renewals/upcoming/summary
```

Exemplo de resposta:

```json
{
  "expired": 2,
  "0_30_days": 5,
  "31_60_days": 3,
  "61_90_days": 4,
  "total": 14
}
```

## Regras implementadas

- `customer_name`, `manager_name`, `vendor_contract_id`, `product_description` e `coverage_end_date` são obrigatórios.
- `quantity` deve ser maior que zero.
- `total_value` não pode ser negativo.
- `vendor_contract_id` deve ser único.
- Listagem suporta paginação e filtros por:
  - `start_date`
  - `end_date`
  - `manager_name`
  - `customer_name`
  - `page`
  - `limit`
- O resumo de vencimentos calcula as faixas de 0–30, 31–60 e 61–90 dias, além de vencidos.

## Testes

Para rodar a suíte de testes:

```powershell
pytest
```

Os testes cobrem casos básicos de saúde da API, criação, leitura, atualização, exclusão e resumo de vencimentos.

## Melhorias futuras

Uma boa melhoria para o projeto seria separar melhor a responsabilidade entre:

- camada de rota/HTTP (FastAPI);
- camada de serviço (regras de negócio);
- camada de persistência (SQLAlchemy / banco de dados);
- camada de cliente ou integração externa, se houver futuramente acesso a serviços ou APIs externas.

Essa separação deixa o código mais organizado, facilita testes e reduz acoplamento entre regras do negócio e transporte HTTP.

Em outras palavras, o ideal é manter a API como camada de entrada/saída, enquanto o service cuida da lógica e o banco cuida da persistência.

## Observações

- O projeto foi estruturado com foco em clareza e organização, seguindo uma separação simples entre API, schemas, modelos e serviços.
- O uso de SQLite foi mantido para facilitar execução local e validação do desafio.
- O arquivo `.env` e o banco local não devem ser versionados no Git.

## Próximo passo sugerido

Se o objetivo for evoluir a solução, a próxima etapa natural seria:

1. melhorar a documentação de endpoints com exemplos reais de payload;
2. reforçar testes de filtros combinados;
3. refinar mensagens de erro e status HTTP;
4. migrar o valor monetário para `Decimal` para maior robustez em cálculos financeiros.
