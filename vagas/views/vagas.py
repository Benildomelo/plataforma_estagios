
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from ..models import Vaga

from ..repositories.aluno_repository import AlunoRepository
from ..repositories.candidatura_repository import CandidaturaRepository
from ..repositories.curso_repository import CursoRepository
from ..repositories.empresa_repository import EmpresaRepository
from ..repositories.vaga_repository import VagaRepository

from ..services.candidatura_service import CandidaturaService
from ..services.vaga_service import VagaService


def _buscar_aluno(request):
    return AlunoRepository.buscar_por_usuario(request.user)


def _buscar_empresa(request):
    return EmpresaRepository.buscar_por_usuario(request.user)


def _buscar_curso(curso_id):
    curso = CursoRepository.buscar_por_id(curso_id)

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
        messages.error(request, str(erro))

    return redirect('detalhe_vaga', vaga_id=vaga_id)


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
            messages.error(request, str(erro))

    return _render_criar_vaga(request, empresa, cursos)


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
        cursos_ids = request.POST.getlist('cursos')

        erro_validacao = None
        bolsa_validada = None
        cursos_selecionados = None

        # Valida os campos obrigatórios e os limites do modelo.
        if not titulo:
            erro_validacao = 'O título da vaga é obrigatório.'
        elif len(titulo) > 200:
            erro_validacao = (
                'O título da vaga não pode ter mais de 200 caracteres.'
            )
        elif not descricao:
            erro_validacao = 'A descrição da vaga é obrigatória.'
        elif not local:
            erro_validacao = 'O local da vaga é obrigatório.'
        elif len(local) > 200:
            erro_validacao = (
                'O local não pode ter mais de 200 caracteres.'
            )
        elif not carga_horaria:
            erro_validacao = 'A carga horária é obrigatória.'
        elif len(carga_horaria) > 50:
            erro_validacao = (
                'A carga horária não pode ter mais de 50 caracteres.'
            )
        elif not cursos_ids:
            erro_validacao = (
                'Selecione pelo menos um curso para a vaga.'
            )

        # Valida a bolsa antes de modificar qualquer dado da vaga.
        if erro_validacao is None and bolsa:
            try:
                bolsa_validada = Decimal(
                    str(bolsa).replace(',', '.')
                )
            except (InvalidOperation, ValueError):
                erro_validacao = (
                    'Informe um valor válido para a bolsa.'
                )
            else:
                if not bolsa_validada.is_finite() or bolsa_validada < 0:
                    erro_validacao = (
                        'A bolsa deve ser um valor igual ou superior a zero.'
                    )
                elif bolsa_validada != bolsa_validada.quantize(Decimal('0.01')):
                    erro_validacao = (
                        'A bolsa pode ter no máximo duas casas decimais.'
                    )
                elif bolsa_validada >= Decimal('100000000'):
                    erro_validacao = (
                        'O valor da bolsa ultrapassa o limite permitido.'
                    )

        # Normaliza e valida os IDs dos cursos.
        if erro_validacao is None:
            cursos_ids_normalizados = list(
                dict.fromkeys(
                    str(curso_id).strip()
                    for curso_id in cursos_ids
                    if str(curso_id).strip()
                )
            )

            if not cursos_ids_normalizados or any(
                not curso_id.isdigit()
                for curso_id in cursos_ids_normalizados
            ):
                erro_validacao = (
                    'Um ou mais cursos selecionados são inválidos.'
                )
            else:
                cursos_selecionados = CursoRepository.buscar_ativos().filter(
                    id__in=cursos_ids_normalizados
                )

                if cursos_selecionados.count() != len(
                    cursos_ids_normalizados
                ):
                    erro_validacao = (
                        'Um ou mais cursos selecionados são inválidos.'
                    )

        if erro_validacao:
            messages.error(request, erro_validacao)

            # Mantém os dados submetidos no formulário sem salvar a vaga.
            vaga_formulario = Vaga(
                id=vaga.id,
                empresa=empresa,
                titulo=titulo,
                descricao=descricao,
                requisitos=requisitos,
                local=local,
                carga_horaria=carga_horaria,
                bolsa=
                    bolsa_validada
                    if bolsa_validada is not None
                    else vaga.bolsa,
                status=vaga.status,
                ativo=vaga.ativo,
                data_publicacao=vaga.data_publicacao,
            )

            return render(
                request,
                'vagas/empresa/editar_vaga.html',
                {
                    'empresa': empresa,
                    'vaga': vaga_formulario,
                    'cursos': cursos,
                    'cursos_selecionados_ids': cursos_ids,
                }
            )

        # Atualiza somente depois de validar todos os campos.
        with transaction.atomic():
            vaga.titulo = titulo
            vaga.descricao = descricao
            vaga.requisitos = requisitos
            vaga.local = local
            vaga.carga_horaria = carga_horaria
            vaga.bolsa = bolsa_validada

            # Uma vaga editada precisa passar novamente pela análise.
            vaga.status = 'PENDENTE'
            vaga.data_publicacao = None

            VagaRepository.atualizar(vaga)
            vaga.cursos.set(cursos_selecionados)

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
            VagaService.encerrar_vaga(vaga, empresa)

            messages.success(
                request,
                'Vaga encerrada com sucesso.'
            )

        except ValueError as erro:
            messages.error(request, str(erro))

    return redirect('area_empresa')
