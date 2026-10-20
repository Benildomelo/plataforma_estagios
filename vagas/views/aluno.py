from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404
from django.core.exceptions import PermissionDenied

from django.contrib import messages
from django.contrib.auth import logout 
from django.shortcuts import redirect, render

from ..repositories.aluno_repository import AlunoRepository
from ..repositories.candidatura_repository import CandidaturaRepository
from ..repositories.curso_repository import CursoRepository
from ..repositories.usuario_repository import UsuarioRepository
from ..repositories.empresa_repository import EmpresaRepository


def _buscar_aluno(request):
    return AlunoRepository.buscar_por_usuario(
        request.user
    )


def _verificar_acesso_aluno(request):
    """
    Garante que o usuário autenticado possui um perfil de aluno ativo.

    Retorna o aluno quando o acesso é permitido.
    Caso contrário, encerra a sessão e direciona para o login de aluno.
    """
    if not request.user.is_authenticated:
        return None

    aluno = _buscar_aluno(request)

    if not aluno or not aluno.ativo:
        logout(request)
        return None

    return aluno


def _render_cadastro(request, cursos):
    return render(
        request,
        'vagas/aluno/cadastro_aluno.html',
        {
            'cursos': cursos,
        }
    )


def minhas_candidaturas(request):
    aluno = _verificar_acesso_aluno(request)

    if not aluno:
        return redirect('entrar_aluno')

    candidaturas = CandidaturaRepository.buscar_por_aluno(
        aluno
    )

    return render(
        request,
        'vagas/aluno/minhas_candidaturas.html',
        {
            'candidaturas': candidaturas,
        }
    )


def area_aluno(request):
    aluno = _verificar_acesso_aluno(request)

    if not aluno:
        return redirect('entrar_aluno')

    candidaturas = CandidaturaRepository.buscar_por_aluno(
        aluno
    )

    return render(
        request,
        'vagas/aluno/area_aluno.html',
        {
            'aluno': aluno,
            'candidaturas': candidaturas,
        }
    )


def cadastro_aluno(request):
    if request.user.is_authenticated:
        aluno = _buscar_aluno(request)

        if aluno and aluno.ativo:
            return redirect('area_aluno')

        logout(request)

    cursos = CursoRepository.buscar_ativos()

    if request.method == 'POST':
        nome = request.POST.get(
            'nome',
            ''
        ).strip()

        matricula = request.POST.get(
            'matricula',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        telefone = request.POST.get(
            'telefone',
            ''
        ).strip()

        curso_id = request.POST.get(
            'curso',
            ''
        ).strip()

        username = request.POST.get(
            'username',
            ''
        ).strip()

        senha = request.POST.get(
            'password',
            ''
        )

        confirmar_senha = request.POST.get(
            'password_confirmacao',
            ''
        )

        if senha != confirmar_senha:
            messages.error(
                request,
                'As senhas não coincidem.'
            )
            return _render_cadastro(
                request,
                cursos
            )

        if len(senha) < 6:
            messages.error(
                request,
                'A senha deve ter pelo menos 6 caracteres.'
            )
            return _render_cadastro(
                request,
                cursos
            )

        if UsuarioRepository.buscar_por_username(
            username
        ):
            messages.error(
                request,
                'Este usuário já existe.'
            )
            return _render_cadastro(
                request,
                cursos
            )

        if UsuarioRepository.buscar_por_email(
            email
        ):
            messages.error(
                request,
                'Este e-mail já está cadastrado.'
            )
            return _render_cadastro(
                request,
                cursos
            )

        if AlunoRepository.buscar_por_matricula(
            matricula
        ):
            messages.error(
                request,
                'Esta matrícula já está cadastrada.'
            )
            return _render_cadastro(
                request,
                cursos
            )

        curso = CursoRepository.buscar_por_id(
            curso_id
        )

        if not curso or not curso.ativo:
            messages.error(
                request,
                'Selecione um curso válido.'
            )
            return _render_cadastro(
                request,
                cursos
            )

        usuario = UsuarioRepository.criar(
            username=username,
            email=email,
            password=senha
        )

        AlunoRepository.criar(
            usuario=usuario,
            nome=nome,
            matricula=matricula,
            email=email,
            telefone=telefone,
            curso=curso,
            ativo=True,
            senha_provisoria=False
        )

        messages.success(
            request,
            'Cadastro realizado com sucesso.'
        )

        return redirect('entrar_aluno')

    return _render_cadastro(
        request,
        cursos
    )


def perfil_aluno(request):
    aluno = _verificar_acesso_aluno(request)

    if not aluno:
        return redirect('entrar_aluno')

    return render(
        request,
        'vagas/aluno/perfil_aluno.html',
        {
            'aluno': aluno,
        }
    )



def curriculo_aluno(request):
    aluno = _verificar_acesso_aluno(request)
    
    if not aluno:
        return redirect('entrar_aluno')

    if request.method == 'POST':
        campos = [
            'objetivo_profissional',
            'resumo_profissional',
            'habilidades',
            'experiencias',
            'cursos_complementares',
        ]

        # Salva as informações digitadas.
        for campo in campos:
            setattr(
                aluno,
                campo,
                request.POST.get(campo, '').strip()
            )

        arquivo = request.FILES.get('curriculo')

        if arquivo:
            nome = Path(arquivo.name).name

            if not nome.lower().endswith('.pdf'):
                messages.error(
                    request,
                    'Envie o currículo em formato PDF.'
                )
                return render(
                    request,
                    'vagas/aluno/curriculo_aluno.html',
                    {'aluno': aluno}
                )

            if arquivo.size > 5 * 1024 * 1024:
                messages.error(
                    request,
                    'O arquivo deve ter no máximo 5 MB.'
                )
                return render(
                    request,
                    'vagas/aluno/curriculo_aluno.html',
                    {'aluno': aluno}
                )

            if arquivo.size == 0:
                messages.error(
                    request,
                    'O arquivo enviado está vazio.'
                )
                return render(
                    request,
                    'vagas/aluno/curriculo_aluno.html',
                    {'aluno': aluno}
                )

            # Confere se o arquivo realmente começa como um PDF.
            inicio = arquivo.read(5)
            arquivo.seek(0)

            if inicio != b'%PDF-':
                messages.error(
                    request,
                    'O arquivo selecionado não parece ser um PDF válido.'
                )
                return render(
                    request,
                    'vagas/aluno/curriculo_aluno.html',
                    {'aluno': aluno}
                )

            aluno.curriculo = arquivo

        aluno.save()

        messages.success(
            request,
            'Currículo atualizado com sucesso!'
        )

        return redirect('curriculo_aluno')

    return render(
        request,
        'vagas/aluno/curriculo_aluno.html',
        {'aluno': aluno}
    )



def editar_perfil_aluno(request):
    aluno = _verificar_acesso_aluno(request)

    if not aluno:
        return redirect('entrar_aluno')

    cursos = CursoRepository.buscar_ativos()

    if request.method == 'POST':
        aluno.nome = request.POST.get(
            'nome',
            aluno.nome
        ).strip()

        aluno.email = request.POST.get(
            'email',
            aluno.email
        ).strip()

        aluno.telefone = request.POST.get(
            'telefone',
            aluno.telefone
        ).strip()

        curso_id = request.POST.get(
            'curso',
            ''
        ).strip()

        if curso_id:
            curso = CursoRepository.buscar_por_id(
                curso_id
            )

            if not curso or not curso.ativo:
                messages.error(
                    request,
                    'Selecione um curso válido.'
                )

                return render(
                    request,
                    'vagas/aluno/editar_perfil_aluno.html',
                    {
                        'aluno': aluno,
                        'cursos': cursos,
                    }
                )

            aluno.curso = curso

        AlunoRepository.atualizar(
            aluno
        )

        messages.success(
            request,
            'Perfil atualizado com sucesso.'
        )

        return redirect('perfil_aluno')

    return render(
        request,
        'vagas/aluno/editar_perfil_aluno.html',
        {
            'aluno': aluno,
            'cursos': cursos,
        }
    )

def visualizar_curriculo(request, aluno_id):
    if not request.user.is_authenticated:
        raise PermissionDenied

    aluno = AlunoRepository.buscar_por_id(aluno_id)

    if not aluno or not aluno.curriculo:
        raise Http404("Currículo não encontrado.")

    # O aluno pode acessar somente o próprio currículo.
    aluno_autenticado = AlunoRepository.buscar_por_usuario(
        request.user
    )

    if aluno_autenticado and aluno_autenticado.ativo:
        if aluno_autenticado.id == aluno.id:
            arquivo = aluno.curriculo.open("rb")
            return FileResponse(               arquivo,
                content_type="application/pdf",
                as_attachment=False,
                filename="curriculo.pdf",
            )

    # A empresa só pode acessar currículos de candidatos
    # a vagas pertencentes a ela.
    empresa = EmpresaRepository.buscar_por_usuario(
        request.user
    )

    if empresa and empresa.ativo:
        tem_candidatura = CandidaturaRepository.buscar_por_empresa(
            empresa
        ).filter(aluno_id=aluno.id).exists()

        if tem_candidatura:
            arquivo = aluno.curriculo.open("rb")
            return FileResponse(
                arquivo,
                content_type="application/pdf",
                as_attachment=False,
                filename="curriculo.pdf",
            )

    raise PermissionDenied