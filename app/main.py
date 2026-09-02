from fastapi import FastAPI
from app.api.contracts import contracts_router

app = FastAPI(
    title="Renewal Tracker",
    description="A aplicação permite cadastrar contratos, consultar"
    "contratos de forma paginada e obter um resumo dos vencimentos por faixa de prazo.",
    version="1.0.0"
)

app.include_router(contracts_router)

@app.get("/")
async def health_check():
    return {"status": "ok"}
