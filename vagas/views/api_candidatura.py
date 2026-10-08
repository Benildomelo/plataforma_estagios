import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..dto.candidatura_dto import (
    CandidaturaRequestDTO,
    CandidaturaResponseDTO,
)
from ..repositories.aluno_repository import AlunoRepository
from ..services.candidatura_service import CandidaturaService


@csrf_exempt
def api_candidatar(request):

    if request.method != "POST":
        return JsonResponse(
            {"erro": "Método não permitido. Use POST."},
            status=405
        )

    try:
        dados = json.loads(request.body)

        dto = CandidaturaRequestDTO(
            aluno_id=dados.get("aluno_id"),
            vaga_id=dados.get("vaga_id")
        )

        aluno = AlunoRepository.buscar_por_id(dto.aluno_id)

        if not aluno:
            return JsonResponse(
                {"erro": "Aluno não encontrado."},
                status=404
            )

        candidatura, criada = CandidaturaService.candidatar(
            aluno,
            dto.vaga_id
        )

        resposta = CandidaturaResponseDTO(
            id=candidatura.id,
            aluno_id=candidatura.aluno_id,
            vaga_id=candidatura.vaga_id,
            status=candidatura.status,
            observacao=candidatura.observacao
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
                }
            },
            status=201 if criada else 200
        )

    except ValueError as erro:
        return JsonResponse(
            {"erro": str(erro)},
            status=400
        )

    except Exception:
        return JsonResponse(
            {"erro": "Dados inválidos."},
            status=400
        )