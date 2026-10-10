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

        # Recebe vários cursos selecionados no formulário.
        cursos_ids = request.POST.getlist('cursos')

        try:
            vaga = VagaService.criar_vaga(
                empresa=empresa,
                titulo=titulo,
                descricao=descricao,
                requisitos=requisitos,
                local=local,
                carga_horaria=carga_horaria,
                bolsa=bolsa,
                cursos_ids=cursos_ids,
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

    vaga = VagaRepository.buscar_por_id(vaga_id)

    if not vaga or vaga.empresa != empresa:
        return redirect('area_empresa')

    cursos = CursoRepository.buscar_ativos()

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        requisitos = request.POST.get('requisitos', '').strip()
        local = request.POST.get('local', '').strip()
        carga_horaria = request.POST.get('carga_horaria', '').strip()
        bolsa = request.POST.get('bolsa', '').strip()

        # Recebe todos os cursos selecionados.
        cursos_ids = request.POST.getlist('cursos')

        # Valida os campos obrigatórios.
        if not titulo:
            messages.error(request, 'O título da vaga é obrigatório.')

        elif not descricao:
            messages.error(request, 'A descrição da vaga é obrigatória.')

        elif not local:
            messages.error(request, 'O local da vaga é obrigatório.')

        elif not carga_horaria:
            messages.error(request, 'A carga horária é obrigatória.')

        elif not cursos_ids:
            messages.error(
                request,
                'Selecione pelo menos um curso para a vaga.'
            )

        else:
            # Busca somente cursos ativos.
            cursos_selecionados = CursoRepository.buscar_ativos().filter(
                id__in=cursos_ids
            )

            # Confere se todos os IDs enviados são válidos.
            if cursos_selecionados.count() != len(set(cursos_ids)):
                messages.error(
                    request,
                    'Um ou mais cursos selecionados são inválidos.'
                )

            else:
                vaga.titulo = titulo
                vaga.descricao = descricao
                vaga.requisitos = requisitos
                vaga.local = local
                vaga.carga_horaria = carga_horaria
                vaga.bolsa = bolsa or None

                # Atualiza os cursos relacionados à vaga.
                vaga.cursos.set(cursos_selecionados)

                # A alteração precisa passar novamente pela análise.
                vaga.status = 'PENDENTE'
                vaga.data_publicacao = None

                VagaRepository.atualizar(vaga)

                messages.success(
                    request,
                    'Vaga atualizada e enviada novamente para análise.'
                )

                return redirect(
                    'detalhe_vaga_empresa',
                    vaga_id=vaga.id
                )

        # Mantém os dados preenchidos se houver erro.
        return render(
            request,
            'vagas/empresa/editar_vaga.html',
            {
                'empresa': empresa,
                'vaga': vaga,
                'cursos': cursos,
                'cursos_selecionados_ids': cursos_ids,
            }
        )

    return render(
        request,
        'vagas/empresa/editar_vaga.html',
        {
            'empresa': empresa,
            'vaga': vaga,
            'cursos': cursos,
            'cursos_selecionados_ids': list(
                vaga.cursos.values_list('id', flat=True)
            ),
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