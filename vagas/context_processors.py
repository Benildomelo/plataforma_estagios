from .models import Aluno, Empresa


def usuario_contexto(request):

    aluno = None
    empresa = None

    if request.user.is_authenticated:

        aluno = Aluno.objects.filter(
            usuario=request.user,
            ativo=True
        ).first()

        if not aluno:
            empresa = Empresa.objects.filter(
                usuario=request.user,
                ativo=True
            ).first()

    return {
        'aluno': aluno,
        'empresa': empresa,
    }