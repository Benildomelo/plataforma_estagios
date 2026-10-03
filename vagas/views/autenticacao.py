from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render

from vagas.models import Aluno



def _realizar_login(request, redirecionamento):
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    usuario = authenticate(
        request,
        username=username,
        password=password
    )

    if usuario is not None:
        login(request, usuario)
        return redirect(redirecionamento)

    messages.error(
        request,
        'Usuário ou senha inválidos.'
    )

    return None


def entrar(request):
    if request.user.is_authenticated:
        return redirect('area_aluno')

    if request.method == 'POST':
        resposta = _realizar_login(
            request,
            'area_aluno'
        )

        if resposta:
            return resposta

    return render(
        request,
        'vagas/autenticacao/login.html'
    )


def entrar_aluno(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is None:
            messages.error(
                request,
                'Usuário ou senha inválidos.'
            )

            return render(
                request,
                'vagas/autenticacao/login_aluno.html'
            )

        if not Aluno.objects.filter(
            usuario=usuario,
            ativo=True
        ).exists():

            messages.error(
                request,
                'Este usuário não possui um perfil de aluno ativo.'
            )

            return render(
                request,
                'vagas/autenticacao/login_aluno.html'
            )

        login(request, usuario)

        return redirect('area_aluno')

    return render(
        request,
        'vagas/autenticacao/login_aluno.html'
    )

def entrar_empresa(request):
    if request.method == 'POST':
        resposta = _realizar_login(
            request,
            'area_empresa'
        )

        if resposta:
            return resposta

    return render(
        request,
        'vagas/autenticacao/login_empresa.html'
    )


def entrar_instituicao(request):

    # Se já estiver logado, verifica se é administrador
    if request.user.is_authenticated:

        if request.user.is_superuser:
            return redirect('area_instituicao')

        messages.error(
            request,
            'Acesso permitido somente para administradores da instituição.'
        )

        logout(request)

        return redirect('entrar_instituicao')

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        # Usuário não existe ou senha incorreta
        if usuario is None:

            messages.error(
                request,
                'Usuário ou senha inválidos.'
            )

            return render(
                request,
                'vagas/autenticacao/login_instituicao.html'
            )

        # Usuário existe, mas não é administrador
        if not usuario.is_superuser:

            messages.error(
                request,
                'Este usuário não possui permissão para acessar a área da instituição.'
            )

            return render(
                request,
                'vagas/autenticacao/login_instituicao.html'
            )

        # Administrador autorizado
        login(
            request,
            usuario
        )

        return redirect(
            'area_instituicao'
        )

    return render(
        request,
        'vagas/autenticacao/login_instituicao.html'
    )


def trocar_senha_empresa(request):

    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    if request.method == 'POST':

        senha_atual = request.POST.get(
            'senha_atual',
            ''
        )

        nova_senha = request.POST.get(
            'nova_senha',
            ''
        )

        confirmar_senha = request.POST.get(
            'confirmar_senha',
            ''
        )

        if not request.user.check_password(senha_atual):

            messages.error(
                request,
                'A senha atual está incorreta.'
            )

            return redirect(
                'trocar_senha_empresa'
            )

        if nova_senha != confirmar_senha:

            messages.error(
                request,
                'As novas senhas não coincidem.'
            )

            return redirect(
                'trocar_senha_empresa'
            )

        if len(nova_senha) < 6:

            messages.error(
                request,
                'A nova senha deve ter pelo menos 6 caracteres.'
            )

            return redirect(
                'trocar_senha_empresa'
            )

        request.user.set_password(
            nova_senha
        )

        request.user.save()

        update_session_auth_hash(
            request,
            request.user
        )

        messages.success(
            request,
            'Senha alterada com sucesso.'
        )

        return redirect(
            'area_empresa'
        )

    return render(
        request,
        'vagas/autenticacao/trocar_senha_empresa.html'
    )


def sair(request):

    logout(request)

    return redirect('inicio')