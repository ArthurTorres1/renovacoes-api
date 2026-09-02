## 1. Contexto e regra principal da avaliação

O Portal Renovações é uma aplicação interna construída com React, FastAPI, PostgreSQL e práticas de desenvolvimento em camadas.

O repositório do Portal Renovações será disponibilizado **somente como material de consulta e exemplo de padrões de engenharia**. Ele não é a base da implementação.

### O que A pessoa deve fazer

A pessoa deverá:

1. criar um repositório próprio;
2. iniciar a API FastAPI do zero;
3. configurar ambiente, dependências e estrutura de diretórios;
4. configurar persistência de dados;
5. inicializar e utilizar o Alembic para controlar a evolução do schema;
6. implementar a funcionalidade descrita neste documento;
7. criar testes automatizados;
8. documentar como executar e validar a entrega.

### O que não é permitido

- Copiar módulos, migrations, modelos, routers, serviços ou testes do Portal Renovações.
- Criar a solução dentro deste repositório ou alterar arquivos do Portal Renovações.
- Entregar apenas arquivos soltos sem uma aplicação executável.
- Manipular a estrutura do banco manualmente sem migration.
- Usar dados em memória como substituto da persistência obrigatória.
- Incluir segredos, tokens, senhas ou arquivos `.env` reais no repositório.

> **Importante:** consultar o Portal Renovações, documentação oficial e materiais técnicos é permitido. O objetivo não é impedir consulta; é avaliar a capacidade de entender referências e construir uma solução própria, justificando as decisões tomadas.

---

## 2. Desafio: API de controle de renovações

Criar uma API REST chamada **Renewal Tracker** para controlar contratos e acompanhar vencimentos próximos.

A aplicação deve permitir cadastrar contratos, consultar contratos de forma paginada e obter um resumo dos vencimentos por faixa de prazo.

### Domínio mínimo

Cada contrato deve possuir, no mínimo:

| Campo                 | Tipo sugerido   | Regra                                |
| --------------------- | --------------- | ------------------------------------ |
| `id`                  | inteiro ou UUID | Identificador gerado pela aplicação. |
| `customer_name`       | texto           | Obrigatório.                         |
| `manager_name`        | texto           | Obrigatório.                         |
| `vendor_contract_id`  | texto           | Obrigatório e único.                 |
| `product_description` | texto           | Obrigatório.                         |
| `coverage_end_date`   | data            | Obrigatório.                         |
| `quantity`            | inteiro         | Obrigatório e maior que zero.        |
| `total_value`         | decimal         | Obrigatório e maior ou igual a zero. |
| `created_at`          | data/hora       | Gerado pela aplicação.               |
| `updated_at`          | data/hora       | Atualizado pela aplicação.           |

A pessoa pode adicionar campos ou criar entidades auxiliares se houver justificativa, mas não deve ampliar o escopo sem necessidade.

---

## 3. Requisitos obrigatórios

### 3.1 Inicialização do projeto

A solução deve ser construída pelA pessoa do início ao fim.

#### Backend

A API deve utilizar:

- Python 3.11 ou superior;
- FastAPI;
- Pydantic para validação e contratos HTTP;
- SQLAlchemy ou outra biblioteca de persistência devidamente justificada;
- Alembic para migrations;
- banco relacional local:
  - SQLite é aceito para simplificar a execução;
  - PostgreSQL é aceito e desejável, mas não obrigatório;
- `pytest` para testes automatizados.

A estrutura do projeto deve separar responsabilidades de modo compreensível. Uma sugestão, não obrigatória, é:

```text
renewal-tracker/
├── app/
│   ├── api/                 # Rotas/controllers HTTP
│   ├── core/                # Configuração e dependências
│   ├── models/              # Modelos ORM
│   ├── schemas/             # Contratos Pydantic
│   ├── services/            # Regras de negócio
│   └── main.py
├── alembic/
├── tests/
├── alembic.ini
├── requirements.txt ou pyproject.toml
├── .env.example
└── README.md
```

A estrutura exata é livre, desde que os limites entre HTTP, regras de negócio e persistência estejam claros.

#### Alembic e schema

A pessoa deve:

1. inicializar o Alembic no repositório;
2. configurar a URL do banco por variável de ambiente ou configuração equivalente;
3. criar ao menos uma migration versionada que gere a tabela principal de contratos;
4. executar a migration para criar o banco local;
5. demonstrar que uma base vazia pode ser criada com o comando de migration documentado;
6. versionar os arquivos de configuração e migrations, sem versionar a base local nem credenciais reais.

> Criar tabelas automaticamente no evento de startup, por exemplo com `metadata.create_all()`, não substitui a migration obrigatória do Alembic.

### 3.2 Endpoints

Implementar os endpoints abaixo.

| Método           | Rota                         | Objetivo                                        |
| ---------------- | ---------------------------- | ----------------------------------------------- |
| `GET`            | `/health`                    | Verificar se a aplicação está disponível.       |
| `POST`           | `/contracts`                 | Cadastrar um contrato.                          |
| `GET`            | `/contracts`                 | Listar contratos de forma paginada e filtrável. |
| `GET`            | `/contracts/{contract_id}`   | Consultar um contrato pelo identificador.       |
| `PUT` ou `PATCH` | `/contracts/{contract_id}`   | Atualizar um contrato existente.                |
| `GET`            | `/renewals/upcoming/summary` | Retornar totais por faixa de vencimento.        |

O prefixo `/api/v1` é opcional, mas, se adotado, deve ser aplicado de forma consistente e documentado.

#### Regras de criação e atualização

1. `customer_name`, `manager_name`, `vendor_contract_id`, `product_description` e `coverage_end_date` são obrigatórios.
2. `quantity` deve ser maior que zero.
3. `total_value` não pode ser negativo.
4. `vendor_contract_id` deve ser único.
5. A tentativa de cadastrar contrato com identificador de fornecedor já existente deve retornar erro HTTP apropriado, sem expor detalhes internos do banco.
6. Consultar ou atualizar um identificador inexistente deve retornar **HTTP 404**.
7. As respostas devem usar schemas Pydantic explícitos; não retornar diretamente objetos internos do ORM.

#### Filtros da lista

O endpoint `GET /contracts` deve aceitar:

| Parâmetro       | Tipo                    | Obrigatório | Regra                                  |
| --------------- | ----------------------- | ----------: | -------------------------------------- |
| `start_date`    | data ISO (`YYYY-MM-DD`) |         não | Data mínima de vencimento.             |
| `end_date`      | data ISO (`YYYY-MM-DD`) |         não | Data máxima de vencimento.             |
| `manager_name`  | texto                   |         não | Filtra por Account Manager.            |
| `customer_name` | texto                   |         não | Filtra por cliente.                    |
| `page`          | inteiro                 |         não | Padrão `1`, mínimo `1`.                |
| `limit`         | inteiro                 |         não | Padrão `25`, mínimo `1`, máximo `100`. |

A resposta deve conter:

```json
{
  "total": 1,
  "page": 1,
  "limit": 25,
  "rows": [
    {
      "id": 1,
      "customer_name": "Cliente Exemplo",
      "manager_name": "Ana Silva",
      "vendor_contract_id": "VC-001",
      "product_description": "Licença de software",
      "coverage_end_date": "2026-12-31",
      "quantity": 10,
      "total_value": "1500.00",
      "created_at": "2026-01-01T10:00:00",
      "updated_at": "2026-01-01T10:00:00"
    }
  ]
}
```

A representação numérica de `total_value` pode ser `number` ou `string` decimal, desde que seja consistente, documentada e preserve precisão adequada.

#### Regras da listagem

1. Quando `start_date` e `end_date` forem informados, validar que `end_date >= start_date`.
2. Caso o intervalo seja inválido, retornar **HTTP 422** com mensagem clara.
3. Aplicar filtros de cliente e gestor de forma combinável.
4. Ordenar de forma determinística:
   - primeiro por `coverage_end_date` crescente;
   - depois por `customer_name` crescente;
   - depois por identificador crescente, se necessário para estabilidade.
5. Calcular corretamente `offset` e `limit`.
6. Não carregar todos os dados em memória para paginar.
7. Consultas devem ser parametrizadas pela biblioteca escolhida; nunca concatenar dados de entrada em SQL.

### 3.3 Resumo de vencimentos

O endpoint `GET /renewals/upcoming/summary` deve retornar contagens de contratos por faixa de vencimento.

Parâmetros aceitos:

- `customer_name` opcional;
- `manager_name` opcional;
- `end_date` opcional, com padrão de hoje + 90 dias.

A resposta deve ter o formato equivalente a:

```json
{
  "expired": 2,
  "0_30_days": 5,
  "31_60_days": 3,
  "61_90_days": 4,
  "total": 14
}
```

Regras:

1. Considerar a data atual como referência para as faixas.
2. `expired`: vencimento anterior a hoje.
3. `0_30_days`: de hoje até hoje + 30 dias, inclusive.
4. `31_60_days`: de hoje + 31 até hoje + 60 dias, inclusive.
5. `61_90_days`: de hoje + 61 até hoje + 90 dias, inclusive.
6. `end_date` limita o período superior analisado; seu padrão deve permitir a faixa completa de 90 dias.
7. O resumo deve respeitar os filtros opcionais de cliente e gestor.
8. `total` deve ser a soma exata das quatro faixas retornadas.

---

## 4. Qualidade, segurança e tratamento de erros

A entrega deve demonstrar práticas básicas de engenharia.

### Requisitos

1. Usar variáveis de ambiente para configurações, especialmente URL do banco.
2. Incluir `.env.example` com valores fictícios e sem segredos.
3. Manter `.env`, arquivos de banco locais, ambientes virtuais, caches e cobertura fora do Git.
4. Validar entradas usando Pydantic e/ou mecanismos apropriados do FastAPI.
5. Retornar status HTTP coerentes:
   - `201` para criação bem-sucedida;
   - `200` para consultas e atualizações bem-sucedidas;
   - `404` para recurso inexistente;
   - `409` ou outro status justificado para conflito de `vendor_contract_id`;
   - `422` para entrada inválida;
   - `500` sem stack trace ou detalhes do banco para falhas inesperadas.
6. Não expor strings de conexão, SQL bruto, stack traces ou detalhes internos nas respostas.
7. Não usar `SELECT *` sem justificativa.
8. Usar tipos adequados para dinheiro e datas; evitar `float` para valores monetários quando a biblioteca escolhida oferecer `Decimal` ou equivalente.
9. Incluir tratamento compreensível para violações de unicidade e outros erros previsíveis de persistência.
10. Manter funções e módulos com responsabilidade clara.

### Diferenciais positivos

Os seguintes itens não são obrigatórios, mas podem ser valorizados se bem executados e sem prejudicar o escopo:

- Docker e Docker Compose;
- PostgreSQL em vez de SQLite;
- lint/format configurado, como Ruff, Black ou equivalente;
- logs estruturados;
- paginação com metadados adicionais;
- seeds idempotentes separados das migrations;
- autenticação simples, se houver tempo e boa justificativa;
- frontend simples consumindo a API.

---

## 5. Testes automatizados

Criar testes com `pytest`. Os testes devem ser reproduzíveis sem depender de banco externo ou credenciais da empresa.

### Casos mínimos

1. O endpoint `/health` responde corretamente.
2. Um contrato válido é criado com sucesso.
3. Campos obrigatórios e regras de `quantity` e `total_value` são validados.
4. Um `vendor_contract_id` duplicado é rejeitado.
5. A consulta de um contrato inexistente retorna 404.
6. A listagem calcula corretamente paginação e `offset`.
7. Filtros por cliente, gestor e período funcionam de forma combinada.
8. `end_date` anterior a `start_date` retorna 422.
9. A ordenação por vencimento e cliente é respeitada.
10. O resumo calcula corretamente as quatro faixas e o total.
11. As respostas atendem aos contratos definidos.

São aceitos testes de API com `FastAPI TestClient`, banco SQLite temporário, fixtures e mocks/fakes. A avaliação valoriza testes que validem comportamento público, não somente detalhes internos de implementação.

---

## 6. Documentação e entregáveis

O repositório da entrega deve conter, no mínimo, um `README.md` objetivo.

### O README deve explicar

1. Objetivo da aplicação.
2. Pré-requisitos.
3. Como criar e ativar ambiente virtual.
4. Como instalar dependências.
5. Como configurar variáveis de ambiente a partir de `.env.example`.
6. Como executar migrations do Alembic.
7. Como iniciar a API localmente.
8. Como executar os testes.
9. Rotas principais e exemplos resumidos de requisição.
10. Decisões técnicas tomadas.
11. Limitações conhecidas.
12. Uma melhoria que seria implementada com mais tempo.

### Entregáveis esperados

1. Repositório Git próprio, criado pelA pessoa.
2. Histórico de commits compreensível e progressivo.
3. API FastAPI executável.
4. Arquivos e configuração do Alembic versionados.
5. Ao menos uma migration funcional aplicada à estrutura da aplicação.
6. Testes automatizados novos e aprovados.
7. `.gitignore` adequado e `.env.example` sem informações sensíveis.
8. Pull request para o repositório indicado pelo avaliador, ou link do repositório conforme orientação.
9. Evidência da aplicação em execução:
   - captura do Swagger/OpenAPI, terminal ou cliente HTTP;
   - demonstração das migrations executadas;
   - demonstração breve dos endpoints principais.
10. Documento de entrega no PR ou no README com decisões, comandos executados e limitações.
