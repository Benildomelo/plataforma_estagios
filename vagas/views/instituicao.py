from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from vagas.models import (
    Aluno,
    Curso,
    Empresa,
    Vaga,
    Candidatura,
)


# =========================================================
# PROTEÇÃO DA ÁREA DA INSTITUIÇÃO
# =========================================================

def somente_instituicao(view_func):
    return user_passes_test(
        lambda user: (
            user.is_authenticated
            and user.is_superuser
        ),
        login_url='/entrar-instituicao/'
    )(view_func)


# =========================================================
# ÁREA PRINCIPAL
# =========================================================

@somente_instituicao
def area_instituicao(request):

    total_alunos = Aluno.objects.filter(
        ativo=True
    ).count()

    total_empresas = Empresa.objects.filter(
        ativo=True
    ).count()

    total_vagas = Vaga.objects.filter(
        ativo=True
    ).count()

    total_candidaturas = Candidatura.objects.count()

    return render(
        request,
        'vagas/instituicao/area_instituicao.html',
        {
            'total_alunos': total_alunos,
            'total_empresas': total_empresas,
            'total_vagas': total_vagas,
            'total_candidaturas': total_candidaturas,
        }
    )


# =========================================================
# GERENCIAR ALUNOS
# =========================================================

@somente_instituicao
def gerenciar_alunos(request):

    alunos = Aluno.objects.select_related(
        'curso'
    ).order_by('nome')

    # PESQUISA
    pesquisa = request.GET.get('q', '').strip()

    if pesquisa:
        alunos = alunos.filter(
            Q(nome__icontains=pesquisa)
            | Q(matricula__icontains=pesquisa)
            | Q(email__icontains=pesquisa)
        )

    # FILTRO POR CURSO
    curso_id = request.GET.get('curso', '').strip()

    if curso_id:
        if curso_id.isdigit():
            alunos = alunos.filter(
                curso_id=int(curso_id)
            )

    # FILTRO POR SITUAÇÃO
    situacao = request.GET.get('situacao', '').strip()

    if situacao == 'ativo':
        alunos = alunos.filter(ativo=True)

    elif situacao == 'inativo':
        alunos = alunos.filter(ativo=False)

    # CONTADORES GERAIS
    total_alunos = Aluno.objects.count()

    total_ativos = Aluno.objects.filter(
        ativo=True
    ).count()

    total_inativos = Aluno.objects.filter(
        ativo=False
    ).count()

    # CURSOS PARA O FILTRO
    cursos = Curso.objects.all().order_by('nome')

    return render(
        request,
        'vagas/instituicao/gerenciar_alunos.html',
        {
            'alunos': alunos,
            'cursos': cursos,
            'pesquisa': pesquisa,
            'curso_selecionado': curso_id,
            'situacao_selecionada': situacao,
            'total_alunos': total_alunos,
            'total_ativos': total_ativos,
            'total_inativos': total_inativos,
        }
    )


# =========================================================
# GERENCIAR EMPRESAS
# =========================================================

@somente_instituicao
def gerenciar_empresas(request):

    empresas = Empresa.objects.all().order_by(
        'nome_fantasia'
    )

    return render(
        request,
        'vagas/instituicao/gerenciar_empresas.html',
        {
            'empresas': empresas,
        }
    )


# =========================================================
# GERENCIAR VAGAS
# =========================================================

@somente_instituicao
def gerenciar_vagas(request):

    vagas = Vaga.objects.select_related(
        'empresa',
        'curso'
    ).order_by('-id')

    return render(
        request,
        'vagas/instituicao/gerenciar_vagas.html',
        {
            'vagas': vagas,
        }
    )


# =========================================================
# DETALHES DA VAGA
# =========================================================

@somente_instituicao
def detalhes_vaga_instituicao(request, vaga_id):

    vaga = get_object_or_404(
        Vaga.objects.select_related(
            'empresa',
            'curso'
        ),
        id=vaga_id
    )

    return render(
        request,
        'vagas/publicas/detalhe_vaga.html',
        {
            'vaga': vaga,
        }
    )


# =========================================================
# APROVAR VAGA
# =========================================================

@somente_instituicao
def aprovar_vaga(request, vaga_id):

    if request.method != 'POST':
        return redirect('gerenciar_vagas')

    vaga = get_object_or_404(
        Vaga,
        id=vaga_id
    )

    vaga.status = 'APROVADA'
    vaga.ativo = True

    vaga.save(
        update_fields=[
            'status',
            'ativo',
        ]
    )

    return redirect('gerenciar_vagas')


# =========================================================
# REJEITAR VAGA
# =========================================================

@somente_instituicao
def rejeitar_vaga(request, vaga_id):

    if request.method != 'POST':
        return redirect('gerenciar_vagas')

    vaga = get_object_or_404(
        Vaga,
        id=vaga_id
    )

    vaga.status = 'REJEITADA'
    vaga.ativo = False

    vaga.save(
        update_fields=[
            'status',
            'ativo',
        ]
    )

    return redirect('gerenciar_vagas')


# =========================================================
# ENCERRAR VAGA
# =========================================================

@somente_instituicao
def encerrar_vaga_instituicao(request, vaga_id):

    if request.method != 'POST':
        return redirect('gerenciar_vagas')

    vaga = get_object_or_404(
        Vaga,
        id=vaga_id
    )

    vaga.status = 'ENCERRADA'
    vaga.ativo = False

    vaga.save(
        update_fields=[
            'status',
            'ativo',
        ]
    )

    return redirect('gerenciar_vagas')


# =========================================================
# REABRIR VAGA
# =========================================================

@somente_instituicao
def reabrir_vaga(request, vaga_id):

    if request.method != 'POST':
        return redirect('gerenciar_vagas')

    vaga = get_object_or_404(
        Vaga,
        id=vaga_id
    )

    vaga.status = 'APROVADA'
    vaga.ativo = True

    vaga.save(
        update_fields=[
            'status',
            'ativo',
        ]
    )

    return redirect('gerenciar_vagas')


# =========================================================
# GERENCIAR CANDIDATURAS
# =========================================================

@somente_instituicao
def gerenciar_candidaturas(request):

    candidaturas = Candidatura.objects.select_related(
        'aluno',
        'vaga',
        'vaga__empresa',
        'vaga__curso'
    ).order_by('-data_candidatura')

    return render(
        request,
        'vagas/instituicao/gerenciar_candidaturas.html',
        {
            'candidaturas': candidaturas,
        }
    )