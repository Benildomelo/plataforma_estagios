from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from vagas.models import Aluno


@login_required(login_url='/entrar/')
def area_instituicao(request):

    total_alunos = Aluno.objects.filter(
        ativo=True
    ).count()

    return render(
        request,
        'vagas/instituicao/area_instituicao.html',
        {
            'total_alunos': total_alunos,
        }
    )


@login_required(login_url='/entrar/')
def gerenciar_alunos(request):

    alunos = Aluno.objects.select_related(
        'curso'
    ).order_by('nome')

    return render(
        request,
        'vagas/instituicao/gerenciar_alunos.html',
        {
            'alunos': alunos,
        }
    )