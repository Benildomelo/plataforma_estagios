from ..models import Curso


class CursoRepository:

    @staticmethod
    def buscar_por_id(curso_id):
        return Curso.objects.filter(
            id=curso_id
        ).first()

    @staticmethod
    def buscar_ativos():
        return Curso.objects.filter(
            ativo=True
        ).order_by('nome')

    @staticmethod
    def buscar_por_nome(nome):
        return Curso.objects.filter(
            nome__iexact=nome
        ).first()

    @staticmethod
    def criar(**dados):
        return Curso.objects.create(
            **dados
        )

    @staticmethod
    def atualizar(curso):
        curso.save()
        return curso