
import json

from django.http import JsonResponse

from ..dto.candidatura_dto import (
    CandidaturaRequestDTO,
    CandidaturaResponseDTO,
)
from ..repositories.aluno_repository import AlunoRepository
from ..services.candidatura_service import CandidaturaService


def api_candidatar(request):
    if request.method != "POST":
        return JsonResponse(
            {"erro": "Método não permitido. Use POST."},
            status=405,
        )

    try:
        dados = json.loads(request.body)

        if not isinstance(dados, dict):
            return JsonResponse(
                {"erro": "O corpo deve ser um objeto JSON."},
                status=400,
            )

        aluno_id = dados.get("aluno_id")
        vaga_id = dados.get("vaga_id")

        if aluno_id is None or vaga_id is None:
            return JsonResponse(
                {"erro": "Informe aluno_id e vaga_id."},
                status=400,
            )

        try:
            aluno_id = int(aluno_id)
            vaga_id = int(vaga_id)
        except (TypeError, ValueError):
            return JsonResponse(
                {"erro": "aluno_id e vaga_id devem ser números inteiros."},
                status=400,
            )

        if aluno_id <= 0 or vaga_id <= 0:
            return JsonResponse(
                {"erro": "Os identificadores devem ser positivos."},
                status=400,
            )

        dto = CandidaturaRequestDTO(
            aluno_id=aluno_id,
            vaga_id=vaga_id,
        )

        aluno = AlunoRepository.buscar_por_id(dto.aluno_id)

        if not aluno:
            return JsonResponse(
                {"erro": "Aluno não encontrado."},
                status=404,
            )

        candidatura, criada = CandidaturaService.candidatar(
            aluno,
            dto.vaga_id,
        )

        resposta = CandidaturaResponseDTO(
            id=candidatura.id,
            aluno_id=candidatura.aluno_id,
            vaga_id=candidatura.vaga_id,
            status=candidatura.status,
            observacao=candidatura.observacao,
        )

        return JsonResponse(
            {
                "criada": criada,
                "candidatura": {
                    "id": resposta.id,
                    "aluno_id": resposta.aluno_id,
                    "vaga_id": resposta.vaga_id,
                    "status": resposta.status,
                    "observacao": resposta.observacao,
                },
            },
            status=202 if criada else 200,
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"erro": "JSON inválido."},
            status=400,
        )
    except ValueError as erro:
        return JsonResponse(
            {"erro": str(erro)},
            status=400,
        )
    except Exception:
        return JsonResponse(
            {"erro": "Não foi possível processar a candidatura."},
            status=500,
        )
