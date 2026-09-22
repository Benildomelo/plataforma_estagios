from django.shortcuts import render, redirect
from django.contrib import messages

from ..repositories.vaga_repository import VagaRepository
from ..repositories.candidatura_repository import CandidaturaRepository
from ..repositories.aluno_repository import AlunoRepository
from ..repositories.empresa_repository import EmpresaRepository
from ..repositories.curso_repository import CursoRepository


def candidatar(request, vaga_id):
    if not request.user.is_authenticated:
        return redirect('entrar_aluno')

    vaga = VagaRepository.buscar_por_id(
        vaga_id
    )

    if not vaga or vaga.status != 'APROVADA' or not vaga.ativo:
        return redirect('vagas_publicas')

    aluno = AlunoRepository.buscar_por_usuario(
        request.user
    )

    if not aluno:
        messages.error(
            request,
            'Perfil do aluno não encontrado.'
        )
        return redirect('entrar_aluno')

    candidatura, criada = _obter_ou_criar_candidatura(
        aluno,
        vaga
    )

    if criada:
        messages.success(
            request,
            'Candidatura realizada com sucesso.'
        )
    else:
        messages.info(
            request,
            'Você já se candidatou a esta vaga.'
        )

    return redirect(
        'detalhe_vaga',
        vaga_id=vaga.id
    )


def _obter_ou_criar_candidatura(aluno, vaga):

    candidatura = CandidaturaRepository.buscar_por_aluno_e_vaga(
        aluno,
        vaga
    )

    if candidatura:
        return candidatura, False

    candidatura = CandidaturaRepository.criar(
        aluno=aluno,
        vaga=vaga
    )

    return candidatura, True


def criar_vaga(request):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = EmpresaRepository.buscar_por_usuario(
        request.user
    )

    if not empresa:
        messages.error(
            request,
            'Perfil da empresa não encontrado.'
        )
        return redirect('entrar_empresa')

    cursos = CursoRepository.buscar_ativos()

    if request.method == 'POST':
        titulo = request.POST.get(
            'titulo',
            ''
        ).strip()

        descricao = request.POST.get(
            'descricao',
            ''
        ).strip()

        requisitos = request.POST.get(
            'requisitos',
            ''
        ).strip()

        local = request.POST.get(
            'local',
            ''
        ).strip()

        carga_horaria = request.POST.get(
            'carga_horaria',
            ''
        ).strip()

        bolsa = request.POST.get(
            'bolsa',
            ''
        ).strip()

        curso_id = request.POST.get(
            'curso',
            ''
        ).strip()

        curso = CursoRepository.buscar_por_id(
            curso_id
        )

        if not curso or not curso.ativo:
            messages.error(
                request,
                'Selecione um curso válido.'
            )

            return render(
                request,
                'vagas/empresa/criar_vaga.html',
                {
                    'empresa': empresa,
                    'cursos': cursos,
                }
            )

        vaga = VagaRepository.criar(
            empresa=empresa,
            titulo=titulo,
            descricao=descricao,
            requisitos=requisitos,
            local=local,
            carga_horaria=carga_horaria,
            bolsa=bolsa or None,
            curso=curso,
            status='PENDENTE',
            ativo=True
        )

        messages.success(
            request,
            'Vaga criada e enviada para análise.'
        )

        return redirect(
            'detalhe_vaga_empresa',
            vaga_id=vaga.id
        )

    return render(
        request,
        'vagas/empresa/criar_vaga.html',
        {
            'empresa': empresa,
            'cursos': cursos,
        }
    )


def editar_vaga(request, vaga_id):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = EmpresaRepository.buscar_por_usuario(
        request.user
    )

    if not empresa:
        return redirect('entrar_empresa')

    vaga = VagaRepository.buscar_por_id(
        vaga_id
    )

    if not vaga or vaga.empresa != empresa:
        return redirect('area_empresa')

    cursos = CursoRepository.buscar_ativos()

    if request.method == 'POST':
        vaga.titulo = request.POST.get(
            'titulo',
            vaga.titulo
        ).strip()

        vaga.descricao = request.POST.get(
            'descricao',
            vaga.descricao
        ).strip()

        vaga.requisitos = request.POST.get(
            'requisitos',
            vaga.requisitos
        ).strip()

        vaga.local = request.POST.get(
            'local',
            vaga.local
        ).strip()

        vaga.carga_horaria = request.POST.get(
            'carga_horaria',
            vaga.carga_horaria
        ).strip()

        bolsa = request.POST.get(
            'bolsa',
            ''
        ).strip()

        vaga.bolsa = bolsa or None

        curso_id = request.POST.get(
            'curso',
            ''
        ).strip()

        if curso_id:
            curso = CursoRepository.buscar_por_id(
                curso_id
            )

            if not curso or not curso.ativo:
                messages.error(
                    request,
                    'Selecione um curso válido.'
                )

                return render(
                    request,
                    'vagas/empresa/editar_vaga.html',
                    {
                        'empresa': empresa,
                        'vaga': vaga,
                        'cursos': cursos,
                    }
                )

            vaga.curso = curso

        vaga.status = 'PENDENTE'

        VagaRepository.atualizar(
            vaga
        )

        messages.success(
            request,
            'Vaga atualizada e enviada novamente para análise.'
        )

        return redirect(
            'detalhe_vaga_empresa',
            vaga_id=vaga.id
        )

    return render(
        request,
        'vagas/empresa/editar_vaga.html',
        {
            'empresa': empresa,
            'vaga': vaga,
            'cursos': cursos,
        }
    )


def encerrar_vaga(request, vaga_id):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = EmpresaRepository.buscar_por_usuario(
        request.user
    )

    if not empresa:
        return redirect('entrar_empresa')

    vaga = VagaRepository.buscar_por_id(
        vaga_id
    )

    if not vaga or vaga.empresa != empresa:
        return redirect('area_empresa')

    if request.method == 'POST':
        VagaRepository.encerrar(
            vaga
        )

        messages.success(
            request,
            'Vaga encerrada com sucesso.'
        )

    return redirect(
        'area_empresa'
    )