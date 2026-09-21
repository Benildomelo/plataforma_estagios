from ..models import Candidatura


class CandidaturaRepository:

    @staticmethod
    def buscar_por_id(candidatura_id):
        return Candidatura.objects.filter(
            id=candidatura_id
        ).first()

    @staticmethod
    def buscar_por_aluno(aluno):
        return Candidatura.objects.filter(
            aluno=aluno
        ).order_by('-data_candidatura')

    @staticmethod
    def buscar_por_vaga(vaga):
        return Candidatura.objects.filter(
            vaga=vaga
        ).order_by('-data_candidatura')

    @staticmethod
    def buscar_por_empresa(empresa):
        return Candidatura.objects.filter(
            vaga__empresa=empresa
        ).order_by('-data_candidatura')

    @staticmethod
    def criar(**dados):
        return Candidatura.objects.create(
            **dados
        )

    @staticmethod
    def atualizar(candidatura):
        candidatura.save()
        return candidatura

    @staticmethod
    def existe(aluno, vaga):
        return Candidatura.objects.filter(
            aluno=aluno,
            vaga=vaga
        ).exists()