from fastapi import FastAPI

app = FastAPI(
    title="UNIPI Conecta - Microserviço"
)


@app.get("/")
def raiz():
    return {
        "servico": "microservico",
        "status": "online"
    }


@app.get("/validar-vaga/{vaga_id}")
def validar_vaga(vaga_id: int):
    return {
        "vaga_id": vaga_id,
        "valida": vaga_id > 0,
        "mensagem": "Vaga validada pelo microserviço."
    }