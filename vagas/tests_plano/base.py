"""Base compartilhada pelos testes do plano: contas e dados fictícios."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from vagas.models import Aluno, Curso, Empresa, Vaga


class BaseTestePlano(TestCase):
    senha = "SenhaTeste123!"

    def setUp(self):
        self.curso = Curso.objects.create(
            nome="Sistemas de Informação",
            ativo=True,
        )

        # Aluno
        self.usuario_aluno = User.objects.create_user(
            username="aluno_teste",
            email="aluno@example.com",
            password=self.senha,
        )
        self.aluno = Aluno.objects.create(
            usuario=self.usuario_aluno,
            nome="Aluno de Teste",
            matricula="MAT001",
            email="aluno@example.com",
            curso=self.curso,
            ativo=True,
        )

        # Empresa A
        self.usuario_empresa = User.objects.create_user(
            username="empresa_a",
            email="empresa.a@example.com",
            password=self.senha,
        )
        self.empresa = Empresa.objects.create(
            usuario=self.usuario_empresa,
            razao_social="Empresa A LTDA",
            nome_fantasia="Empresa A",
            cnpj="11111111000111",
            email="empresa.a@example.com",
            ativo=True,
        )

        # Empresa B (para testes de acesso entre empresas)
        self.usuario_empresa_b = User.objects.create_user(
            username="empresa_b",
            email="empresa.b@example.com",
            password=self.senha,
        )
        self.empresa_b = Empresa.objects.create(
            usuario=self.usuario_empresa_b,
            razao_social="Empresa B LTDA",
            nome_fantasia="Empresa B",
            cnpj="22222222000122",
            email="empresa.b@example.com",
            ativo=True,
        )

        # Usuário sem perfil de aluno nem de empresa
        self.usuario_comum = User.objects.create_user(
            username="usuario_comum",
            email="comum@example.com",
            password=self.senha,
        )

        # Instituição = superusuário
        self.admin = User.objects.create_superuser(
            username="admin_teste",
            email="admin@example.com",
            password=self.senha,
        )

    def criar_vaga(self, empresa=None, **extra):
        dados = {
            "titulo": "Estágio em Desenvolvimento",
            "descricao": "Descrição da vaga de teste.",
            "requisitos": "Python",
            "carga_horaria": "20h semanais",
            "local": "Teresina",
            "empresa": empresa or self.empresa,
            "status": "APROVADA",
            "ativo": True,
            "data_publicacao": timezone.now(),
        }
        dados.update(extra)
        vaga = Vaga.objects.create(**dados)
        vaga.cursos.add(self.curso)
        return vaga
