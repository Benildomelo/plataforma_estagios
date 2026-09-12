from django.shortcuts import render, redirect, get_object_or_404
from .models import Vaga, Candidatura, Aluno, Empresa, Curso
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone


def inicio(request):
    aluno = None
    empresa = None
    candidaturas = []

    if request.user.is_authenticated:

        aluno = Aluno.objects.filter(
            usuario=request.user,
            ativo=True
        ).first()

        if aluno:
            candidaturas = Candidatura.objects.filter(
                aluno=aluno
            ).select_related(
                'vaga',
                'vaga__empresa'
            ).order_by('-data_candidatura')

        else:
            empresa = Empresa.objects.filter(
                usuario=request.user,
                ativo=True
            ).first()

    return render(
        request,
        'vagas/inicio.html',
        {
            'aluno': aluno,
            'empresa': empresa,
            'candidaturas': candidaturas,
        }
    )


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

def entrar_aluno(request):
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

            if Aluno.objects.filter(
                usuario=usuario,
                ativo=True
            ).exists():

                login(request, usuario)

                return redirect('area_aluno')

            mensagem = 'Esta conta não possui acesso de aluno.'

        else:
            mensagem = 'Usuário ou senha inválidos.'

    return render(
        request,
        'vagas/login_aluno.html',
        {
            'mensagem': mensagem
        }
    )

def entrar_empresa(request):
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

            if Empresa.objects.filter(
                usuario=usuario,
                ativo=True
            ).exists():

                login(request, usuario)

                return redirect('area_empresa')

            mensagem = 'Esta conta não possui acesso de empresa.'

        else:
            mensagem = 'Usuário ou senha inválidos.'

    return render(
        request,
        'vagas/login_empresa.html',
        {
            'mensagem': mensagem
        }
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

def detalhe_vaga_empresa(request, vaga_id):

    if not request.user.is_authenticated:
        return redirect('entrar')

    if not Empresa.objects.filter(
        usuario=request.user,
        ativo=True
    ).exists():
        return redirect('inicio')

    empresa = Empresa.objects.get(
        usuario=request.user,
        ativo=True
    )

    # Busca somente uma vaga pertencente à empresa logada
    vaga = get_object_or_404(
        Vaga,
        id=vaga_id,
        empresa=empresa
    )

    return render(
        request,
        'vagas/detalhe_vaga_empresa.html',
        {
            'empresa': empresa,
            'vaga': vaga,
        }
    )

def editar_vaga(request, vaga_id):

    if not request.user.is_authenticated:
        return redirect('entrar')

    if not Empresa.objects.filter(
        usuario=request.user,
        ativo=True
    ).exists():
        return redirect('inicio')

    empresa = Empresa.objects.get(
        usuario=request.user,
        ativo=True
    )

    # A empresa só pode editar suas próprias vagas
    vaga = get_object_or_404(
        Vaga,
        id=vaga_id,
        empresa=empresa
    )

    # Vaga encerrada não pode mais ser editada
    if vaga.status == 'ENCERRADA':

        messages.error(
            request,
            'Esta vaga já foi encerrada e não pode mais ser editada.'
        )

        return redirect('area_empresa')

    cursos = Curso.objects.filter(
        ativo=True
    ).order_by('nome')


    if request.method == 'POST':

        titulo = request.POST.get(
            'titulo',
            ''
        ).strip()

        descricao = request.POST.get(
            'descricao',
            ''
        ).strip()

        requisitos = request.POST.get(
            'requisitos',
            ''
        ).strip()

        bolsa = request.POST.get(
            'bolsa',
            ''
        ).strip()

        carga_horaria = request.POST.get(
            'carga_horaria',
            ''
        ).strip()

        local = request.POST.get(
            'local',
            ''
        ).strip()

        curso_id = request.POST.get(
            'curso',
            ''
        ).strip()


        # ---------------------------------------------
        # VALIDAÇÃO DOS CAMPOS OBRIGATÓRIOS
        # ---------------------------------------------

        if not titulo or not descricao or not carga_horaria or not local or not curso_id:

            return render(
                request,
                'vagas/editar_vaga.html',
                {
                    'empresa': empresa,
                    'vaga': vaga,
                    'cursos': cursos,
                    'mensagem': 'Preencha todos os campos obrigatórios.'
                }
            )


        # ---------------------------------------------
        # VALIDAÇÃO DO CURSO
        # ---------------------------------------------

        try:

            curso = Curso.objects.get(
                id=curso_id,
                ativo=True
            )

        except Curso.DoesNotExist:

            return render(
                request,
                'vagas/editar_vaga.html',
                {
                    'empresa': empresa,
                    'vaga': vaga,
                    'cursos': cursos,
                    'mensagem': 'O curso selecionado é inválido.'
                }
            )


        # ---------------------------------------------
        # VALIDAÇÃO DA BOLSA
        # ---------------------------------------------

        if bolsa:

            try:

                bolsa = float(bolsa)

                if bolsa < 0:
                    raise ValueError

            except ValueError:

                return render(
                    request,
                    'vagas/editar_vaga.html',
                    {
                        'empresa': empresa,
                        'vaga': vaga,
                        'cursos': cursos,
                        'mensagem': 'Informe um valor válido para a bolsa.'
                    }
                )

        else:

            bolsa = None


        # ---------------------------------------------
        # ATUALIZA OS DADOS DA VAGA
        # ---------------------------------------------

        vaga.titulo = titulo
        vaga.descricao = descricao
        vaga.requisitos = requisitos
        vaga.bolsa = bolsa
        vaga.carga_horaria = carga_horaria
        vaga.local = local
        vaga.curso = curso


        # ---------------------------------------------
        # IMPORTANTE:
        #
        # Depois de editar, a vaga volta para PENDENTE.
        # O administrador deverá aprovar novamente.
        # ---------------------------------------------

        vaga.status = 'PENDENTE'
        vaga.data_publicacao = None
        vaga.ativo = True

        vaga.save()


        messages.success(
            request,
            'Vaga alterada com sucesso! Ela será analisada novamente pelo administrador.'
        )

        return redirect('area_empresa')


    return render(
        request,
        'vagas/editar_vaga.html',
        {
            'empresa': empresa,
            'vaga': vaga,
            'cursos': cursos,
        }
    )

def encerrar_vaga(request, vaga_id):

    if not request.user.is_authenticated:
        return redirect('entrar')

    if not Empresa.objects.filter(
        usuario=request.user,
        ativo=True
    ).exists():
        return redirect('inicio')

    empresa = Empresa.objects.get(
        usuario=request.user,
        ativo=True
    )

    # Só permite encerrar vagas da própria empresa
    vaga = get_object_or_404(
        Vaga,
        id=vaga_id,
        empresa=empresa
    )


    if request.method == 'POST':

        vaga.status = 'ENCERRADA'
        vaga.ativo = False
        vaga.data_encerramento = timezone.now()

        vaga.save()

        messages.success(
            request,
            'A vaga foi encerrada com sucesso.'
        )


    return redirect('area_empresa')


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

def cadastro_aluno(request):
    mensagem = ''

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        matricula = request.POST.get('matricula', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        curso_id = request.POST.get('curso', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        password_confirmacao = request.POST.get('password_confirmacao')

        if password != password_confirmacao:
            mensagem = 'As senhas não são iguais.'

        elif User.objects.filter(username=username).exists():
            mensagem = 'Este nome de usuário já está sendo usado.'

        elif User.objects.filter(email=email).exists():
            mensagem = 'Este e-mail já está sendo usado.'

        elif Aluno.objects.filter(matricula=matricula).exists():
            mensagem = 'Esta matrícula já está cadastrada.'

        elif Aluno.objects.filter(email=email).exists():
            mensagem = 'Este e-mail já está cadastrado.'

        else:
            curso = Curso.objects.get(id=curso_id)

            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            Aluno.objects.create(
                usuario=usuario,
                nome=nome,
                matricula=matricula,
                email=email,
                telefone=telefone,
                curso=curso,
                ativo=True
            )

            return redirect('entrar')

    cursos = Curso.objects.filter(ativo=True)

    return render(
        request,
        'vagas/cadastro_aluno.html',
        {
            'cursos': cursos,
            'mensagem': mensagem,
        }
    )

def perfil_aluno(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    aluno = Aluno.objects.filter(
        usuario=request.user,
        ativo=True
    ).first()

    if not aluno:
        return redirect('inicio')

    return render(
        request,
        'vagas/perfil_aluno.html',
        {
            'aluno': aluno,
        }
    )

def curriculo_aluno(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    aluno = Aluno.objects.filter(
        usuario=request.user,
        ativo=True
    ).first()

    if not aluno:
        return redirect('inicio')

    if request.method == 'POST':
        curriculo = request.FILES.get('curriculo')

        if not curriculo:
            messages.error(
                request,
                'Selecione um arquivo.'
            )
        else:
            aluno.curriculo = curriculo
            aluno.save()

            messages.success(
                request,
                'Currículo enviado com sucesso!'
            )

            return redirect('perfil_aluno')

    return render(
        request,
        'vagas/curriculo_aluno.html',
        {
            'aluno': aluno,
        }
    )

def editar_perfil_aluno(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    aluno = Aluno.objects.filter(
        usuario=request.user,
        ativo=True
    ).first()

    if not aluno:
        return redirect('inicio')

    cursos = Curso.objects.filter(
        ativo=True
    ).order_by('nome')

    mensagem = ''

    if request.method == 'POST':

        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        curso_id = request.POST.get('curso', '').strip()

        if not nome or not email or not curso_id:

            mensagem = 'Preencha todos os campos obrigatórios.'

        elif Aluno.objects.filter(
            email=email
        ).exclude(
            id=aluno.id
        ).exists():

            mensagem = 'Este e-mail já está sendo usado por outro aluno.'

        elif User.objects.filter(
            email=email
        ).exclude(
            id=request.user.id
        ).exists():

            mensagem = 'Este e-mail já está sendo usado por outro usuário.'

        else:

            try:
                curso = Curso.objects.get(
                    id=curso_id,
                    ativo=True
                )

            except Curso.DoesNotExist:

                mensagem = 'O curso selecionado é inválido.'

            else:

                aluno.nome = nome
                aluno.email = email
                aluno.telefone = telefone
                aluno.curso = curso

                aluno.save()

                request.user.email = email
                request.user.save()

                messages.success(
                    request,
                    'Perfil atualizado com sucesso!'
                )

                return redirect('perfil_aluno')

    return render(
        request,
        'vagas/editar_perfil_aluno.html',
        {
            'aluno': aluno,
            'cursos': cursos,
            'mensagem': mensagem,
        }
    )

def perfil_empresa(request):
    if not request.user.is_authenticated:
        return redirect('entrar')

    empresa = Empresa.objects.filter(
        usuario=request.user,
        ativo=True
    ).first()

    if not empresa:
        return redirect('inicio')

    return render(
        request,
        'vagas/perfil_empresa.html',
        {
            'empresa': empresa,
        }
    )