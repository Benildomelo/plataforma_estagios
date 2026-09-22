from django.contrib import messages
from django.shortcuts import redirect, render

from ..repositories.candidatura_repository import CandidaturaRepository
from ..repositories.empresa_repository import EmpresaRepository
from ..repositories.vaga_repository import VagaRepository


def _buscar_empresa(request):
    return EmpresaRepository.buscar_por_usuario(
        request.user
    )


def area_empresa(request):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = _buscar_empresa(request)

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

    empresa = _buscar_empresa(request)

    if not empresa:
        return redirect('entrar_empresa')

    vaga = VagaRepository.buscar_por_id(
        vaga_id
    )

    if not vaga or vaga.empresa != empresa:
        messages.error(
            request,
            'Vaga não encontrada ou não pertence à sua empresa.'
        )
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



def perfil_empresa(request):
    if not request.user.is_authenticated:
        return redirect('entrar_empresa')

    empresa = _buscar_empresa(request)

    if not empresa:
        messages.error(
            request,
            'Perfil da empresa não encontrado.'
        )
        return redirect('entrar_empresa')

    return render(
        request,
        'vagas/empresa/perfil_empresa.html',
        {
            'empresa': empresa,
        }
    )