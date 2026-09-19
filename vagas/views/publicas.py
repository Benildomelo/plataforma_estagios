from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from ..models import Vaga, Candidatura, Aluno, Curso


def inicio(request):
    vagas = Vaga.objects.filter(
        status='APROVADA',
        ativo=True
    ).select_related(
        'empresa',
        'curso'
    )[:6]

    return render(
        request,
        'vagas/publicas/inicio.html',
        {
            'vagas': vagas,
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

    if busca:
        vagas = vagas.filter(
            Q(titulo__icontains=busca) |
            Q(descricao__icontains=busca) |
            Q(empresa__nome_fantasia__icontains=busca)
        )

    if curso_id:
        vagas = vagas.filter(curso_id=curso_id)

    if local:
        vagas = vagas.filter(local__icontains=local)

    return render(
        request,
        'vagas/publicas/lista_vagas.html',
        {
            'vagas': vagas,
            'cursos': cursos,
            'busca': busca,
            'curso_id': curso_id,
            'local': local,
        }
    )


def detalhe_vaga(request, vaga_id):
    vaga = get_object_or_404(
        Vaga.objects.select_related(
            'empresa',
            'curso'
        ),
        id=vaga_id,
        status='APROVADA',
        ativo=True
    )

    ja_candidatou = False

    if request.user.is_authenticated:
        try:
            aluno = Aluno.objects.get(usuario=request.user)
            ja_candidatou = Candidatura.objects.filter(
                vaga=vaga,
                aluno=aluno
            ).exists()
        except Aluno.DoesNotExist:
            pass

    return render(
        request,
        'vagas/publicas/detalhe_vaga.html',
        {
            'vaga': vaga,
            'ja_candidatou': ja_candidatou,
        }
    )