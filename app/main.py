from fastapi import FastAPI

from app.routers import salas

app = FastAPI(
    title="API de Reservas de Salas e Laboratórios",
    description="API REST para gerenciamento de salas e reservas.",
    version="1.0.0"
)

app.include_router(salas.router)


@app.get("/", tags=["Status"])
def home():
    return {"mensagem": "API de Reservas em funcionamento"}