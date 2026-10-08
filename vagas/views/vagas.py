from django.contrib import messages
from django.shortcuts import redirect, render

from ..repositories.aluno_repository import AlunoRepository
from ..repositories.candidatura_repository import CandidaturaRepository
from ..repositories.curso_repository import CursoRepository
from ..repositories.empresa_repository import EmpresaRepository
from ..repositories.vaga_repository import VagaRepository

from ..services.candidatura_service import CandidaturaService
from ..services.vaga_service import VagaService



def _buscar_aluno(request):
    return AlunoRepository.buscar_por_usuario(
        request.user
    )


def _buscar_empresa(request):
    return EmpresaRepository.buscar_por_usuario(
        request.user
    )


def _buscar_curso(curso_id):
    curso = CursoRepository.buscar_por_id(
        curso_id
    )

    if not curso or not curso.ativo:
        return None

    return curso


def _render_criar_vaga(request, empresa, cursos):
    return render(
        request,
        'vagas/empresa/criar_vaga.html',
        {
            'empresa': empresa,
            'cursos': cursos,
        }
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


def candidatar(request, vaga_id):
    if not request.user.is_authenticated:
        return redirect('entrar_aluno')

    aluno = _buscar_aluno(request)

    if not aluno:
        messages.error(
            request,
            'Perfil do aluno não encontrado.'
        )
        return redirect('entrar_aluno')

    try:
        _, criada = CandidaturaService.candidatar(
            aluno,
            vaga_id
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

    except ValueError as erro:
        messages.error(
            request,
            str(erro)
        )

    return redirect(
        'detalhe_vaga',
        vaga_id=vaga_id
    )

def criar_vaga(request):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = _buscar_empresa(request)

    if not empresa:
        messages.error(
            request,
            'Perfil da empresa não encontrado.'
        )
        return redirect('entrar_empresa')

    cursos = CursoRepository.buscar_ativos()

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        requisitos = request.POST.get('requisitos', '').strip()
        local = request.POST.get('local', '').strip()
        carga_horaria = request.POST.get('carga_horaria', '').strip()
        bolsa = request.POST.get('bolsa', '').strip()
        curso_id = request.POST.get('curso', '').strip()

        try:
            vaga = VagaService.criar_vaga(
                empresa=empresa,
                titulo=titulo,
                descricao=descricao,
                requisitos=requisitos,
                local=local,
                carga_horaria=carga_horaria,
                bolsa=bolsa,
                curso_id=curso_id
            )

            messages.success(
                request,
                'Vaga criada e enviada para análise.'
            )

            return redirect(
                'detalhe_vaga_empresa',
                vaga_id=vaga.id
            )

        except ValueError as erro:
            messages.error(
                request,
                str(erro)
            )

    return _render_criar_vaga(
        request,
        empresa,
        cursos
    )


def editar_vaga(request, vaga_id):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = _buscar_empresa(request)

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
            curso = _buscar_curso(
                curso_id
            )

            if not curso:
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

    empresa = _buscar_empresa(request)

    if not empresa:
        return redirect('entrar_empresa')

    vaga = VagaRepository.buscar_por_id(vaga_id)

    if not vaga:
        return redirect('area_empresa')

    if request.method == 'POST':
        try:
            VagaService.encerrar_vaga(
                vaga,
                empresa
            )

            messages.success(
                request,
                'Vaga encerrada com sucesso.'
            )

        except ValueError as erro:
            messages.error(
                request,
                str(erro)
            )

    return redirect('area_empresa')