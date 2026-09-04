from django.shortcuts import render
from .models import Vaga, Candidatura, Aluno, Empresa, Curso
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q


def inicio(request):
    return render(request, 'vagas/inicio.html')


def lista_vagas(request):

    vagas = Vaga.objects.filter(
        status='APROVADA',
        ativo=True
    ).select_related(
        'empresa',
        'curso'
    )

    cursos = Curso.objects.filter(
        ativo=True
    ).order_by('nome')

    busca = request.GET.get('busca', '').strip()
    curso_id = request.GET.get('curso', '').strip()
    local = request.GET.get('local', '').strip()

    # Pesquisa por título, descrição ou empresa
    if busca:
        vagas = vagas.filter(
            Q(titulo__icontains=busca) |
            Q(descricao__icontains=busca) |
            Q(empresa__nome_fantasia__icontains=busca)
        )

    # Filtro por curso
    if curso_id:
        vagas = vagas.filter(
            curso_id=curso_id
        )

    # Filtro por local
    if local:
        vagas = vagas.filter(
            local__icontains=local
        )

    return render(
        request,
        'vagas/lista_vagas.html',
        {
            'vagas': vagas,
            'cursos': cursos,
            'busca': busca,
            'curso_id': curso_id,
            'local': local,
        }
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
    ).select_related(
        'vaga',
        'vaga__empresa'
    )

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

        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        requisitos = request.POST.get('requisitos', '').strip()
        bolsa = request.POST.get('bolsa', '').strip()
        carga_horaria = request.POST.get('carga_horaria', '').strip()
        local = request.POST.get('local', '').strip()
        curso_id = request.POST.get('curso', '').strip()

        # Verifica campos obrigatórios
        if not titulo or not descricao or not carga_horaria or not local or not curso_id:
            return render(
                request,
                'vagas/criar_vaga.html',
                {
                    'empresa': empresa,
                    'cursos': cursos,
                    'mensagem': 'Preencha todos os campos obrigatórios.'
                }
            )

        # Verifica se o curso existe e está ativo
        try:
            curso = Curso.objects.get(
                id=curso_id,
                ativo=True
            )
        except Curso.DoesNotExist:
            return render(
                request,
                'vagas/criar_vaga.html',
                {
                    'empresa': empresa,
                    'cursos': cursos,
                    'mensagem': 'O curso selecionado é inválido.'
                }
            )

        # Valida o valor da bolsa
        if bolsa:
            try:
                bolsa = float(bolsa)

                if bolsa < 0:
                    raise ValueError

            except ValueError:
                return render(
                    request,
                    'vagas/criar_vaga.html',
                    {
                        'empresa': empresa,
                        'cursos': cursos,
                        'mensagem': 'Informe um valor válido para a bolsa.'
                    }
                )
        else:
            bolsa = None

        # Cria a vaga
        Vaga.objects.create(
            titulo=titulo,
            descricao=descricao,
            requisitos=requisitos,
            bolsa=bolsa,
            carga_horaria=carga_horaria,
            local=local,
            empresa=empresa,
            curso=curso,
            status='PENDENTE',
            ativo=True
        )

        messages.success(
            request,
            'Vaga cadastrada com sucesso! Ela será analisada pelo administrador.'
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