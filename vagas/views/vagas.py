from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from ..models import Vaga, Candidatura, Aluno, Empresa


def candidatar(request, vaga_id):
    if not request.user.is_authenticated:
        return redirect('entrar_aluno')

    vaga = get_object_or_404(
        Vaga,
        id=vaga_id,
        status='APROVADA',
        ativo=True
    )

    aluno = get_object_or_404(
        Aluno,
        usuario=request.user
    )

    candidatura, criada = Candidatura.objects.get_or_create(
        vaga=vaga,
        aluno=aluno
    )

    if criada:
        messages.success(
            request,
            'Candidatura realizada com sucesso.'
        )
    else:
        messages.info(
            request,
            'Você já se candidatou a esta vaga.'
        )

    return redirect(
        'detalhe_vaga',
        vaga_id=vaga.id
    )


def criar_vaga(request):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = get_object_or_404(
        Empresa,
        usuario=request.user
    )

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        requisitos = request.POST.get('requisitos', '').strip()
        local = request.POST.get('local', '').strip()
        carga_horaria = request.POST.get('carga_horaria', '').strip()
        bolsa = request.POST.get('bolsa', '').strip()
        curso_id = request.POST.get('curso')

        vaga = Vaga.objects.create(
            empresa=empresa,
            titulo=titulo,
            descricao=descricao,
            requisitos=requisitos,
            local=local,
            carga_horaria=carga_horaria,
            bolsa=bolsa,
            curso_id=curso_id,
            status='PENDENTE',
            ativo=True
        )

        messages.success(
            request,
            'Vaga criada e enviada para análise.'
        )

        return redirect(
            'detalhe_vaga_empresa',
            vaga_id=vaga.id
        )

    return render(
        request,
        'vagas/criar_vaga.html'
    )


def editar_vaga(request, vaga_id):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = get_object_or_404(
        Empresa,
        usuario=request.user
    )

    vaga = get_object_or_404(
        Vaga,
        id=vaga_id,
        empresa=empresa
    )

    if request.method == 'POST':
        vaga.titulo = request.POST.get(
            'titulo',
            vaga.titulo
        ).strip()

        vaga.descricao = request.POST.get(
            'descricao',
            vaga.descricao
        ).strip()

        vaga.requisitos = request.POST.get(
            'requisitos',
            vaga.requisitos
        ).strip()

        vaga.local = request.POST.get(
            'local',
            vaga.local
        ).strip()

        vaga.carga_horaria = request.POST.get(
            'carga_horaria',
            vaga.carga_horaria
        ).strip()

        vaga.bolsa = request.POST.get(
            'bolsa',
            vaga.bolsa
        ).strip()

        curso_id = request.POST.get('curso')

        if curso_id:
            vaga.curso_id = curso_id

        vaga.status = 'PENDENTE'
        vaga.save()

        messages.success(
            request,
            'Vaga atualizada e enviada novamente para análise.'
        )

        return redirect(
            'detalhe_vaga_empresa',
            vaga_id=vaga.id
        )

    return render(
        request,
        'vagas/editar_vaga.html',
        {
            'vaga': vaga,
        }
    )


def encerrar_vaga(request, vaga_id):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = get_object_or_404(
        Empresa,
        usuario=request.user
    )

    vaga = get_object_or_404(
        Vaga,
        id=vaga_id,
        empresa=empresa
    )

    if request.method == 'POST':
        vaga.ativo = False
        vaga.save()

        messages.success(
            request,
            'Vaga encerrada com sucesso.'
        )

    return redirect('area_empresa')