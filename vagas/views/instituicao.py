from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from vagas.models import (
    Aluno,
    Empresa,
    Vaga,
    Candidatura,
)


# =========================================================
# VERIFICAÇÃO DE ADMINISTRADOR
# =========================================================

def somente_administrador(user):

    return (
        user.is_authenticated
        and user.is_superuser
    )


# =========================================================
# ÁREA PRINCIPAL DA INSTITUIÇÃO
# =========================================================

@user_passes_test(
    somente_administrador,
    login_url='/entrar-instituicao/'
)
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

@user_passes_test(
    somente_administrador,
    login_url='/entrar-instituicao/'
)
def gerenciar_alunos(request):

    alunos = Aluno.objects.select_related(
        'curso'
    ).order_by(
        'nome'
    )

    return render(
        request,
        'vagas/instituicao/gerenciar_alunos.html',
        {
            'alunos': alunos,
        }
    )


# =========================================================
# GERENCIAR EMPRESAS
# =========================================================

@user_passes_test(
    somente_administrador,
    login_url='/entrar-instituicao/'
)
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

@user_passes_test(
    somente_administrador,
    login_url='/entrar-instituicao/'
)
def gerenciar_vagas(request):

    vagas = Vaga.objects.select_related(
        'empresa',
        'curso'
    ).order_by(
        '-id'
    )

    return render(
        request,
        'vagas/instituicao/gerenciar_vagas.html',
        {
            'vagas': vagas,
        }
    )


# =========================================================
# GERENCIAR CANDIDATURAS
# =========================================================

@user_passes_test(
    somente_administrador,
    login_url='/entrar-instituicao/'
)
def gerenciar_candidaturas(request):

    candidaturas = Candidatura.objects.select_related(
        'aluno',
        'vaga',
        'vaga__empresa',
        'vaga__curso'
    ).order_by(
        '-data_candidatura'
    )

    return render(
        request,
        'vagas/instituicao/gerenciar_candidaturas.html',
        {
            'candidaturas': candidaturas,
        }
    )