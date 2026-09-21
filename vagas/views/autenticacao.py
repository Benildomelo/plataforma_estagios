from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash


def entrar(request):
    if request.user.is_authenticated:
        return redirect('area_aluno')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect('area_aluno')

        messages.error(
            request,
            'Usuário ou senha inválidos.'
        )

    return render(
        request,
        'vagas/autenticacao/login.html'
    )


def entrar_aluno(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect('area_aluno')

        messages.error(
            request,
            'Usuário ou senha inválidos.'
        )

    return render(
        request,
        'vagas/autenticacao/login_aluno.html'
    )


def entrar_empresa(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect('area_empresa')

        messages.error(
            request,
            'Usuário ou senha inválidos.'
        )

    return render(
        request,
        'vagas/autenticacao/login_empresa.html'
    )


def trocar_senha_empresa(request):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not request.user.check_password(senha_atual):
            messages.error(
                request,
                'A senha atual está incorreta.'
            )
            return redirect('trocar_senha_empresa')

        if nova_senha != confirmar_senha:
            messages.error(
                request,
                'As novas senhas não coincidem.'
            )
            return redirect('trocar_senha_empresa')

        if len(nova_senha) < 6:
            messages.error(
                request,
                'A nova senha deve ter pelo menos 6 caracteres.'
            )
            return redirect('trocar_senha_empresa')

        request.user.set_password(nova_senha)
        request.user.save()

        update_session_auth_hash(
            request,
            request.user
        )

        messages.success(
            request,
            'Senha alterada com sucesso.'
        )

        return redirect('area_empresa')

    return render(
        request,
        'vagas/autenticacao/trocar_senha_empresa.html'
    )


def sair(request):
    logout(request)
    return redirect('inicio')