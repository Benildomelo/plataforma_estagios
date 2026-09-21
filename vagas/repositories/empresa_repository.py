from ..models import Empresa


class EmpresaRepository:

    @staticmethod
    def buscar_por_id(empresa_id):
        return Empresa.objects.filter(
            id=empresa_id
        ).first()

    @staticmethod
    def buscar_por_usuario(usuario):
        return Empresa.objects.filter(
            usuario=usuario
        ).first()

    @staticmethod
    def buscar_por_cnpj(cnpj):
        return Empresa.objects.filter(
            cnpj=cnpj
        ).first()

    @staticmethod
    def buscar_ativas():
        return Empresa.objects.filter(
            ativo=True
        ).order_by('nome_fantasia')

    @staticmethod
    def criar(**dados):
        return Empresa.objects.create(
            **dados
        )

    @staticmethod
    def atualizar(empresa):
        empresa.save()
        return empresa