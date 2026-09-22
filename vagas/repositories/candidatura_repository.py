from ..models import Candidatura


class CandidaturaRepository:

    @staticmethod
    def buscar_por_id(candidatura_id):
        return Candidatura.objects.filter(
            id=candidatura_id
        ).select_related(
            'aluno',
            'vaga',
            'vaga__empresa'
        ).first()

    @staticmethod
    def buscar_por_aluno(aluno):
        return Candidatura.objects.filter(
            aluno=aluno
        ).select_related(
            'vaga',
            'vaga__empresa'
        ).order_by(
            '-data_candidatura'
        )

    @staticmethod
    def buscar_por_vaga(vaga):
        return Candidatura.objects.filter(
            vaga=vaga
        ).select_related(
            'aluno'
        ).order_by(
            '-data_candidatura'
        )

    @staticmethod
    def buscar_por_aluno_e_vaga(aluno, vaga):
        return Candidatura.objects.filter(
            aluno=aluno,
            vaga=vaga
        ).first()

    @staticmethod
    def buscar_por_empresa(empresa):
        return Candidatura.objects.filter(
            vaga__empresa=empresa
        ).select_related(
            'aluno',
            'vaga'
        ).order_by(
            '-data_candidatura'
        )

    @staticmethod
    def criar(**dados):
        return Candidatura.objects.create(
            **dados
        )

    @staticmethod
    def atualizar(candidatura):
        candidatura.save()
        return candidatura