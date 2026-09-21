from ..models import Aluno


class AlunoRepository:

    @staticmethod
    def buscar_por_id(aluno_id):
        return Aluno.objects.filter(
            id=aluno_id
        ).first()

    @staticmethod
    def buscar_por_usuario(usuario):
        return Aluno.objects.filter(
            usuario=usuario
        ).first()

    @staticmethod
    def buscar_por_matricula(matricula):
        return Aluno.objects.filter(
            matricula=matricula
        ).first()

    @staticmethod
    def buscar_ativos():
        return Aluno.objects.filter(
            ativo=True
        ).order_by('nome')

    @staticmethod
    def buscar_por_curso(curso):
        return Aluno.objects.filter(
            curso=curso,
            ativo=True
        ).order_by('nome')

    @staticmethod
    def criar(**dados):
        return Aluno.objects.create(
            **dados
        )

    @staticmethod
    def atualizar(aluno):
        aluno.save()
        return aluno