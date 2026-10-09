from django.contrib import messages
from django.shortcuts import redirect, render

from ..repositories.candidatura_repository import CandidaturaRepository
from ..repositories.empresa_repository import EmpresaRepository
from ..repositories.vaga_repository import VagaRepository
from ..repositories.usuario_repository import UsuarioRepository 


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

def cadastro_empresa(request):
    if request.user.is_authenticated:
        return redirect('area_empresa')

    if request.method == 'POST':
        razao_social = request.POST.get('razao_social', '').strip()
        nome_fantasia = request.POST.get('nome_fantasia', '').strip()
        cnpj = request.POST.get('cnpj', '').strip()
        email = request.POST.get('email', '').strip().lower()
        telefone = request.POST.get('telefone', '').strip()
        endereco = request.POST.get('endereco', '').strip()
        username = request.POST.get('username', '').strip()
        senha = request.POST.get('password', '')
        confirmar_senha = request.POST.get('password_confirmacao', '')

        # Remove pontos, barras, traços e outros caracteres do CNPJ.
        cnpj_limpo = ''.join(caractere for caractere in cnpj if caractere.isdigit())

        if not all([
            razao_social,
            nome_fantasia,
            cnpj,
            email,
            username,
            senha,
            confirmar_senha,
        ]):
            messages.error(request, 'Preencha todos os campos obrigatórios.')

        elif len(cnpj_limpo) != 14:
            messages.error(request, 'Informe um CNPJ com 14 dígitos.')

        elif len(senha) < 6:
            messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')

        elif senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')

        elif UsuarioRepository.buscar_por_username(username):
            messages.error(request, 'Este nome de usuário já está em uso.')

        elif UsuarioRepository.buscar_por_email(email):
            messages.error(request, 'Este e-mail já está vinculado a um usuário.')

        elif EmpresaRepository.buscar_por_cnpj(cnpj_limpo):
            messages.error(request, 'Já existe uma empresa cadastrada com este CNPJ.')

        elif EmpresaRepository.buscar_por_email(email):
            messages.error(request, 'Já existe uma empresa cadastrada com este e-mail.')

        else:
            usuario = UsuarioRepository.criar(
                username=username,
                email=email,
                password=senha,
            )

            EmpresaRepository.criar(
                usuario=usuario,
                razao_social=razao_social,
                nome_fantasia=nome_fantasia,
                cnpj=cnpj_limpo,
                email=email,
                telefone=telefone,
                endereco=endereco,
                ativo=True,
                senha_provisoria=False,
            )

            messages.success(
                request,
                'Cadastro realizado com sucesso! Entre com seu usuário e senha.'
            )
            return redirect('entrar_empresa')

    return render(
        request,
        'vagas/empresa/cadastro_empresa.html'
    )
