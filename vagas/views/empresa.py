from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ..models import Vaga, Candidatura, Empresa


def area_empresa(request):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = Empresa.objects.filter(
        usuario=request.user
    ).first()

    if not empresa:
        messages.error(
            request,
            'Perfil da empresa não encontrado.'
        )
        return redirect('entrar_empresa')

    vagas = Vaga.objects.filter(
        empresa=empresa
    ).order_by('-id')

    return render(
        request,
        'vagas/empresa/area_empresa.html',
        {
            'empresa': empresa,
            'vagas': vagas,
        }
    )


def detalhe_vaga_empresa(request, vaga_id):
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

    candidaturas = Candidatura.objects.filter(
        vaga=vaga
    ).select_related(
        'aluno',
        'aluno__usuario'
    ).order_by('-id')

    return render(
        request,
        'vagas/empresa/detalhe_vaga_empresa.html',
        {
            'vaga': vaga,
            'candidaturas': candidaturas,
        }
    )


def atualizar_candidatura(request, candidatura_id):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    candidatura = get_object_or_404(
        Candidatura,
        id=candidatura_id
    )

    empresa = get_object_or_404(
        Empresa,
        usuario=request.user
    )

    if candidatura.vaga.empresa != empresa:
        messages.error(
            request,
            'Você não tem permissão para alterar esta candidatura.'
        )
        return redirect('area_empresa')

    if request.method == 'POST':
        status = request.POST.get('status')

        candidatura.status = status
        candidatura.save()

        messages.success(
            request,
            'Candidatura atualizada com sucesso.'
        )

    return redirect(
        'detalhe_vaga_empresa',
        vaga_id=candidatura.vaga.id
    )


def perfil_empresa(request):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = Empresa.objects.filter(
        usuario=request.user
    ).first()

    if not empresa:
        return redirect('entrar_empresa')

    return render(
        request,
        'vagas/empresa/perfil_empresa.html',
        {
            'empresa': empresa,
        }
    )