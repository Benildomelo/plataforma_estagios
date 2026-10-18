
import httpx


MICROSERVICO_URL = "http://127.0.0.1:8004"


def validar_vaga(vaga_id):
    url = f"{MICROSERVICO_URL}/validar-vaga/{vaga_id}"

    try:
        resposta = httpx.get(
            url,
            timeout=5.0,
        )
        resposta.raise_for_status()
        dados = resposta.json()

    except httpx.RequestError:
        raise ValueError(
            "O microserviço está indisponível."
        ) from None

    except httpx.HTTPStatusError:
        raise ValueError(
            "O microserviço retornou um erro."
        ) from None

    except ValueError:
        raise ValueError(
            "O microserviço retornou uma resposta inválida."
        ) from None

    if not isinstance(dados, dict):
        raise ValueError(
            "O microserviço retornou uma resposta inválida."
        )

    if not isinstance(dados.get("valida"), bool):
        raise ValueError(
            "O microserviço retornou uma resposta incompleta."
        )

    return dados
