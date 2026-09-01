from django.shortcuts import render
from .models import Vaga, Candidatura, Aluno
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect


def inicio(request):
    return render(request, 'vagas/inicio.html')


def lista_vagas(request):
    vagas = Vaga.objects.filter(
        status='APROVADA',
        ativo=True
    )

    return render(
        request,
        'vagas/lista_vagas.html',
        {'vagas': vagas}
    )

def detalhe_vaga(request, vaga_id):
    vaga = Vaga.objects.get(
        id=vaga_id,
        status='APROVADA',
        ativo=True
    )

    candidatura_existente = None

    if request.user.is_authenticated:
        candidatura_existente = Candidatura.objects.filter(
            aluno__usuario=request.user,
            vaga=vaga
        ).first()

    return render(
        request,
        'vagas/detalhe_vaga.html',
        {
            'vaga': vaga,
            'candidatura_existente': candidatura_existente
        }
    )


def candidatar(request, vaga_id):
    if not request.user.is_authenticated:
        return redirect('entrar')

    vaga = Vaga.objects.get(
        id=vaga_id,
        status='APROVADA',
        ativo=True
    )

    aluno = Aluno.objects.get(usuario=request.user)

    candidatura, criada = Candidatura.objects.get_or_create(
        aluno=aluno,
        vaga=vaga
    )

    return redirect('detalhe_vaga', vaga_id=vaga.id)


def entrar(request):
    mensagem = ''

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
            return redirect('inicio')

        mensagem = 'Usuário ou senha inválidos.'

    return render(
        request,
        'vagas/login.html',
        {'mensagem': mensagem}
    )

def minhas_candidaturas(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    aluno = Aluno.objects.get(usuario=request.user)

    candidaturas = Candidatura.objects.filter(
        aluno=aluno
    ).select_related('vaga', 'vaga__empresa')

    return render(
        request,
        'vagas/minhas_candidaturas.html',
        {
            'candidaturas': candidaturas
        }
    )


def sair(request):
    logout(request)
    return redirect('inicio')

def area_aluno(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    aluno = Aluno.objects.get(usuario=request.user)

    candidaturas = Candidatura.objects.filter(
        aluno=aluno
    ).select_related('vaga', 'vaga__empresa')

    return render(
        request,
        'vagas/area_aluno.html',
        {
            'aluno': aluno,
            'candidaturas': candidaturas,
        }
    )

def area_empresa(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    empresa = Empresa.objects.get(usuario=request.user)

    vagas = Vaga.objects.filter(
        empresa=empresa
    ).order_by('-id')

    return render(
        request,
        'vagas/area_empresa.html',
        {
            'empresa': empresa,
            'vagas': vagas,
        }
    )