from django.db.models import Q

from ..models import Vaga


class VagaRepository:

    @staticmethod
    def buscar_por_id(vaga_id):
        return Vaga.objects.filter(
            id=vaga_id
        ).first()

    @staticmethod
    def buscar_por_empresa(empresa):
        return Vaga.objects.filter(
            empresa=empresa
        ).order_by('-id')

    @staticmethod
    def buscar_aprovadas():
        return Vaga.objects.filter(
            status='APROVADA',
            ativo=True
        ).select_related(
            'empresa',
            'curso'
        ).order_by(
            '-data_publicacao'
        )

    @staticmethod
    def buscar_aprovadas_com_filtros(
        busca='',
        curso_id=None,
        local=''
    ):
        vagas = Vaga.objects.filter(
            status='APROVADA',
            ativo=True
        ).select_related(
            'empresa',
            'curso'
        )

        if busca:
            vagas = vagas.filter(
                Q(titulo__icontains=busca) |
                Q(descricao__icontains=busca) |
                Q(empresa__nome_fantasia__icontains=busca)
            )

        if curso_id:
            vagas = vagas.filter(
                curso_id=curso_id
            )

        if local:
            vagas = vagas.filter(
                local__icontains=local
            )

        return vagas

    @staticmethod
    def buscar_por_curso(curso):
        return Vaga.objects.filter(
            curso=curso,
            status='APROVADA',
            ativo=True
        ).order_by(
            '-data_publicacao'
        )

    @staticmethod
    def buscar_pendentes():
        return Vaga.objects.filter(
            status='PENDENTE',
            ativo=True
        ).order_by(
            '-id'
        )

    @staticmethod
    def criar(**dados):
        return Vaga.objects.create(
            **dados
        )

    @staticmethod
    def atualizar(vaga):
        vaga.save()
        return vaga

    @staticmethod
    def encerrar(vaga):
        vaga.ativo = False
        vaga.status = 'ENCERRADA'

        vaga.save()

        return vaga