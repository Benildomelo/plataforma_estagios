from .repositories.aluno_repository import AlunoRepository
from .repositories.empresa_repository import EmpresaRepository


def usuario_contexto(request):

    aluno = None
    empresa = None

    if request.user.is_authenticated:

        aluno = AlunoRepository.buscar_por_usuario(
            request.user
        )

        if aluno and not aluno.ativo:
            aluno = None

        if not aluno:
            empresa = EmpresaRepository.buscar_por_usuario(
                request.user
            )

            if empresa and not empresa.ativo:
                empresa = None

    return {
        'aluno': aluno,
        'empresa': empresa,
    }