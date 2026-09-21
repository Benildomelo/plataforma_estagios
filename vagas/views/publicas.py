from django.shortcuts import render, redirect

from ..repositories.vaga_repository import VagaRepository
from ..repositories.curso_repository import CursoRepository
from ..repositories.aluno_repository import AlunoRepository
from ..repositories.candidatura_repository import CandidaturaRepository


def inicio(request):
    vagas = VagaRepository.buscar_aprovadas().select_related(
        'empresa',
        'curso'
    )[:6]

    return render(
        request,
        'vagas/publicas/inicio.html',
        {
            'vagas': vagas,
        }
    )


def lista_vagas(request):
    busca = request.GET.get(
        'busca',
        ''
    ).strip()

    curso_id = request.GET.get(
        'curso',
        ''
    ).strip()

    local = request.GET.get(
        'local',
        ''
    ).strip()

    vagas = VagaRepository.buscar_aprovadas_com_filtros(
        busca=busca,
        curso_id=curso_id or None,
        local=local
    )

    cursos = CursoRepository.buscar_ativos()

    return render(
        request,
        'vagas/publicas/lista_vagas.html',
        {
            'vagas': vagas,
            'cursos': cursos,
            'busca': busca,
            'curso_id': curso_id,
            'local': local,
        }
    )


def detalhe_vaga(request, vaga_id):
    vaga = VagaRepository.buscar_por_id(
        vaga_id
    )

    if not vaga or vaga.status != 'APROVADA' or not vaga.ativo:
        return redirect('lista_vagas')

    ja_candidatou = False

    if request.user.is_authenticated:
        aluno = AlunoRepository.buscar_por_usuario(
            request.user
        )

        if aluno:
            ja_candidatou = (
                CandidaturaRepository.buscar_por_vaga(
                    vaga
                ).filter(
                    aluno=aluno
                ).exists()
            )

    return render(
        request,
        'vagas/publicas/detalhe_vaga.html',
        {
            'vaga': vaga,
            'ja_candidatou': ja_candidatou,
        }
    )