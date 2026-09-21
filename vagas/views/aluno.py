from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from ..repositories.aluno_repository import AlunoRepository
from ..repositories.candidatura_repository import CandidaturaRepository
from ..repositories.curso_repository import CursoRepository


def minhas_candidaturas(request):
    if not request.user.is_authenticated:
        return redirect('entrar_aluno')

    aluno = AlunoRepository.buscar_por_usuario(
        request.user
    )

    if not aluno:
        messages.error(
            request,
            'Perfil de aluno não encontrado.'
        )
        return redirect('area_aluno')

    candidaturas = CandidaturaRepository.buscar_por_aluno(
        aluno
    ).select_related(
        'vaga',
        'vaga__empresa'
    )

    return render(
        request,
        'vagas/aluno/minhas_candidaturas.html',
        {
            'candidaturas': candidaturas,
        }
    )


def area_aluno(request):
    if not request.user.is_authenticated:
        return redirect('entrar_aluno')

    aluno = AlunoRepository.buscar_por_usuario(
        request.user
    )

    if not aluno:
        return redirect('cadastro_aluno')

    candidaturas = CandidaturaRepository.buscar_por_aluno(
        aluno
    ).select_related(
        'vaga',
        'vaga__empresa'
    )

    return render(
        request,
        'vagas/aluno/area_aluno.html',
        {
            'aluno': aluno,
            'candidaturas': candidaturas,
        }
    )


def cadastro_aluno(request):
    if request.user.is_authenticated:
        return redirect('area_aluno')

    cursos = CursoRepository.buscar_ativos()

    if request.method == 'POST':
        nome = request.POST.get(
            'nome',
            ''
        ).strip()

        matricula = request.POST.get(
            'matricula',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        telefone = request.POST.get(
            'telefone',
            ''
        ).strip()

        curso_id = request.POST.get(
            'curso',
            ''
        ).strip()

        username = request.POST.get(
            'username',
            ''
        ).strip()

        senha = request.POST.get(
            'password',
            ''
        )

        confirmar_senha = request.POST.get(
            'password_confirmacao',
            ''
        )

        if senha != confirmar_senha:
            messages.error(
                request,
                'As senhas não coincidem.'
            )
            return render(
                request,
                'vagas/aluno/cadastro_aluno.html',
                {
                    'cursos': cursos,
                }
            )

        if len(senha) < 6:
            messages.error(
                request,
                'A senha deve ter pelo menos 6 caracteres.'
            )
            return render(
                request,
                'vagas/aluno/cadastro_aluno.html',
                {
                    'cursos': cursos,
                }
            )

        if User.objects.filter(
            username=username
        ).exists():
            messages.error(
                request,
                'Este usuário já existe.'
            )
            return render(
                request,
                'vagas/aluno/cadastro_aluno.html',
                {
                    'cursos': cursos,
                }
            )

        if User.objects.filter(
            email=email
        ).exists():
            messages.error(
                request,
                'Este e-mail já está cadastrado.'
            )
            return render(
                request,
                'vagas/aluno/cadastro_aluno.html',
                {
                    'cursos': cursos,
                }
            )

        if AlunoRepository.buscar_por_matricula(
            matricula
        ):
            messages.error(
                request,
                'Esta matrícula já está cadastrada.'
            )
            return render(
                request,
                'vagas/aluno/cadastro_aluno.html',
                {
                    'cursos': cursos,
                }
            )

        curso = CursoRepository.buscar_por_id(
            curso_id
        )

        if not curso:
            messages.error(
                request,
                'Curso selecionado inválido.'
            )
            return render(
                request,
                'vagas/aluno/cadastro_aluno.html',
                {
                    'cursos': cursos,
                }
            )

        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=senha
        )

        AlunoRepository.criar(
            usuario=usuario,
            nome=nome,
            matricula=matricula,
            email=email,
            telefone=telefone,
            curso=curso
        )

        messages.success(
            request,
            'Cadastro realizado com sucesso.'
        )

        return redirect('entrar_aluno')

    return render(
        request,
        'vagas/aluno/cadastro_aluno.html',
        {
            'cursos': cursos,
        }
    )


def perfil_aluno(request):
    if not request.user.is_authenticated:
        return redirect('entrar_aluno')

    aluno = AlunoRepository.buscar_por_usuario(
        request.user
    )

    if not aluno:
        return redirect('cadastro_aluno')

    return render(
        request,
        'vagas/aluno/perfil_aluno.html',
        {
            'aluno': aluno,
        }
    )


def curriculo_aluno(request):
    if not request.user.is_authenticated:
        return redirect('entrar_aluno')

    aluno = AlunoRepository.buscar_por_usuario(
        request.user
    )

    if not aluno:
        return redirect('cadastro_aluno')

    return render(
        request,
        'vagas/aluno/curriculo_aluno.html',
        {
            'aluno': aluno,
        }
    )


def editar_perfil_aluno(request):
    if not request.user.is_authenticated:
        return redirect('entrar_aluno')

    aluno = AlunoRepository.buscar_por_usuario(
        request.user
    )

    if not aluno:
        return redirect('cadastro_aluno')

    if request.method == 'POST':
        aluno.nome = request.POST.get(
            'nome',
            aluno.nome
        ).strip()

        aluno.email = request.POST.get(
            'email',
            aluno.email
        ).strip()

        aluno.telefone = request.POST.get(
            'telefone',
            aluno.telefone
        ).strip()

        curso_id = request.POST.get(
            'curso'
        )

        if curso_id:
            curso = CursoRepository.buscar_por_id(
                curso_id
            )

            if curso:
                aluno.curso = curso

        AlunoRepository.atualizar(
            aluno
        )

        messages.success(
            request,
            'Perfil atualizado com sucesso.'
        )

        return redirect('perfil_aluno')

    cursos = CursoRepository.buscar_ativos()

    return render(
        request,
        'vagas/aluno/editar_perfil_aluno.html',
        {
            'aluno': aluno,
            'cursos': cursos,
        }
    )