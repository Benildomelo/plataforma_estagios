from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ..models import Candidatura
from ..repositories.empresa_repository import EmpresaRepository
from ..repositories.vaga_repository import VagaRepository
from ..repositories.candidatura_repository import CandidaturaRepository


def area_empresa(request):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = EmpresaRepository.buscar_por_usuario(
        request.user
    )

    if not empresa:
        messages.error(
            request,
            'Perfil da empresa não encontrado.'
        )
        return redirect('entrar_empresa')

    vagas = VagaRepository.buscar_por_empresa(
        empresa
    )

    candidaturas = CandidaturaRepository.buscar_por_empresa(
        empresa
    )

    return render(
        request,
        'vagas/empresa/area_empresa.html',
        {
            'empresa': empresa,
            'vagas': vagas,
            'candidaturas': candidaturas,
        }
    )


def detalhe_vaga_empresa(request, vaga_id):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = EmpresaRepository.buscar_por_usuario(
        request.user
    )

    if not empresa:
        return redirect('entrar_empresa')

    vaga = VagaRepository.buscar_por_id(
        vaga_id
    )

    if not vaga or vaga.empresa != empresa:
        return redirect('area_empresa')

    candidaturas = CandidaturaRepository.buscar_por_vaga(
        vaga
    )

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

    empresa = EmpresaRepository.buscar_por_usuario(
        request.user
    )

    if not empresa:
        return redirect('entrar_empresa')

    candidatura = CandidaturaRepository.buscar_por_id(
        candidatura_id
    )

    if not candidatura:
        return redirect('area_empresa')

    if candidatura.vaga.empresa != empresa:
        messages.error(
            request,
            'Você não tem permissão para alterar esta candidatura.'
        )
        return redirect('area_empresa')

    if request.method == 'POST':
        status = request.POST.get('status')

        candidatura.status = status

        CandidaturaRepository.atualizar(
            candidatura
        )

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

    empresa = EmpresaRepository.buscar_por_usuario(
        request.user
    )

    if not empresa:
        return redirect('entrar_empresa')

    return render(
        request,
        'vagas/empresa/perfil_empresa.html',
        {
            'empresa': empresa,
        }
    )