from django.shortcuts import render
from .models import Vaga, Candidatura, Aluno, Empresa, Curso
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

    if not Aluno.objects.filter(usuario=request.user).exists():
        return redirect('inicio')

    vaga = Vaga.objects.get(
        id=vaga_id,
        status='APROVADA',
        ativo=True
    )

    if request.method == 'POST':
        aluno = Aluno.objects.get(usuario=request.user)

        Candidatura.objects.get_or_create(
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

            if usuario.is_superuser:
                return redirect('/admin/')

            if Aluno.objects.filter(usuario=usuario).exists():
                return redirect('area_aluno')

            if Empresa.objects.filter(usuario=usuario).exists():
                return redirect('area_empresa')

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

    if not Aluno.objects.filter(usuario=request.user).exists():
        return redirect('inicio')

    aluno = Aluno.objects.get(usuario=request.user)

    candidaturas = Candidatura.objects.filter(
        aluno=aluno
    ).select_related(
        'vaga',
        'vaga__empresa'
    )

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

    if not Aluno.objects.filter(usuario=request.user).exists():
        return redirect('inicio')

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

    if not Empresa.objects.filter(usuario=request.user).exists():
        return redirect('inicio')

    empresa = Empresa.objects.get(usuario=request.user)

    vagas = Vaga.objects.filter(
        empresa=empresa
    ).order_by('-id')

    candidaturas = Candidatura.objects.filter(
        vaga__empresa=empresa
    ).select_related(
        'aluno',
        'vaga'
    ).order_by('-data_candidatura')

    return render(
        request,
        'vagas/area_empresa.html',
        {
            'empresa': empresa,
            'vagas': vagas,
            'candidaturas': candidaturas,
        }
    )

def criar_vaga(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    if not Empresa.objects.filter(usuario=request.user).exists():
        return redirect('inicio')

    empresa = Empresa.objects.get(usuario=request.user)

    cursos = Curso.objects.filter(ativo=True)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        requisitos = request.POST.get('requisitos')
        bolsa = request.POST.get('bolsa')
        carga_horaria = request.POST.get('carga_horaria')
        local = request.POST.get('local')
        curso_id = request.POST.get('curso')

        curso = Curso.objects.get(id=curso_id)

        Vaga.objects.create(
            titulo=titulo,
            descricao=descricao,
            requisitos=requisitos,
            bolsa=bolsa if bolsa else None,
            carga_horaria=carga_horaria,
            local=local,
            empresa=empresa,
            curso=curso,
            status='PENDENTE',
            ativo=True
        )

        return redirect('area_empresa')

    return render(
        request,
        'vagas/criar_vaga.html',
        {
            'empresa': empresa,
            'cursos': cursos,
        }
    )

def atualizar_candidatura(request, candidatura_id):
    if not request.user.is_authenticated:
        return redirect('entrar')

    if not Empresa.objects.filter(usuario=request.user).exists():
        return redirect('inicio')

    empresa = Empresa.objects.get(usuario=request.user)

    candidatura = Candidatura.objects.get(
        id=candidatura_id,
        vaga__empresa=empresa
    )

    if request.method == 'POST':
        novo_status = request.POST.get('status')

        status_permitidos = [
            'EM_ANALISE',
            'APROVADA',
            'REJEITADA',
            'CANCELADA'
        ]

        if novo_status in status_permitidos:
            candidatura.status = novo_status
            candidatura.save()

    return redirect('area_empresa')