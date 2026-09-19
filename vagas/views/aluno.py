from django.shortcuts import render, redirect
from django.contrib import messages

from ..models import Candidatura, Aluno, Vaga


def minhas_candidaturas(request):
    if not request.user.is_authenticated:
        return redirect('entrar_aluno')

    aluno = Aluno.objects.filter(
        usuario=request.user
    ).first()

    if not aluno:
        messages.error(
            request,
            'Perfil de aluno não encontrado.'
        )
        return redirect('area_aluno')

    candidaturas = Candidatura.objects.filter(
        aluno=aluno
    ).select_related(
        'vaga',
        'vaga__empresa'
    ).order_by('-data_candidatura')

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

    aluno = Aluno.objects.filter(
        usuario=request.user
    ).first()

    if not aluno:
        return redirect('cadastro_aluno')

    candidaturas = Candidatura.objects.filter(
        aluno=aluno
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

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        senha = request.POST.get('senha', '')
        confirmar_senha = request.POST.get('confirmar_senha', '')

        if senha != confirmar_senha:
            messages.error(
                request,
                'As senhas não coincidem.'
            )
            return render(
                request,
                'vagas/aluno/cadastro_aluno.html'
            )

        if len(senha) < 6:
            messages.error(
                request,
                'A senha deve ter pelo menos 6 caracteres.'
            )
            return render(
                request,
                'vagas/aluno/cadastro_aluno.html'
            )

        from django.contrib.auth.models import User

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                'Este usuário já existe.'
            )
            return render(
                request,
                'vagas/aluno/cadastro_aluno.html'
            )

        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                'Este e-mail já está cadastrado.'
            )
            return render(
                request,
                'vagas/aluno/cadastro_aluno.html'
            )

        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=senha
        )

        Aluno.objects.create(
            usuario=usuario,
            nome=nome,
            email=email
        )

        messages.success(
            request,
            'Cadastro realizado com sucesso.'
        )

        return redirect('entrar_aluno')

    return render(
        request,
        'vagas/aluno/cadastro_aluno.html'
    )


def perfil_aluno(request):
    if not request.user.is_authenticated:
        return redirect('entrar_aluno')

    aluno = Aluno.objects.filter(
        usuario=request.user
    ).first()

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

    aluno = Aluno.objects.filter(
        usuario=request.user
    ).first()

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

    aluno = Aluno.objects.filter(
        usuario=request.user
    ).first()

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

        aluno.curso = request.POST.get(
            'curso',
            aluno.curso
        ).strip()

        aluno.semestre = request.POST.get(
            'semestre',
            aluno.semestre
        ).strip()

        aluno.save()

        messages.success(
            request,
            'Perfil atualizado com sucesso.'
        )

        return redirect('perfil_aluno')

    return render(
        request,
        'vagas/aluno/editar_perfil_aluno.html',
        {
            'aluno': aluno,
        }
    )
