import httpx


MICROSERVICO_URL = "http://127.0.0.1:8004"


def validar_vaga(vaga_id):
    url = f"{MICROSERVICO_URL}/validar-vaga/{vaga_id}"

    try:
        resposta = httpx.get(
            url,
            timeout=5.0
        )
        resposta.raise_for_status()

    except httpx.RequestError:
        raise ValueError(
            "O microserviço está indisponível."
        )

    return resposta.json()