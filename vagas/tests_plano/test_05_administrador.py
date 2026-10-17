
"""
Setor 5: Administrador Geral / Suporte
ADM-01 a ADM-06: acesso, permissões e segurança.
"""
from django.contrib.auth.models import User
from django.urls import reverse

from .base import BaseTestePlano


class TestesAdministrador(BaseTestePlano):

    def test_ADM_01_superusuario_acessa_painel(self):
        """ADM-01: superusuário autenticado acessa o painel."""
        self.client.force_login(self.admin)

        resposta = self.client.get(reverse("admin:index"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Administração do Site")

    def test_ADM_02_usuario_comum_nao_acessa_painel(self):
        """ADM-02: usuário comum não acessa o painel."""
        self.client.force_login(self.usuario_comum)

        resposta = self.client.get(reverse("admin:index"))

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/admin/login/", resposta.url)

    def test_ADM_03_usuario_staff_sem_permissoes_nao_gerencia_modelos(self):
        """ADM-03: ser staff não concede permissão aos modelos."""
        usuario_staff = User.objects.create_user(
            username="staff_sem_permissoes",
            email="staff@example.com",
            password=self.senha,
            is_staff=True,
            is_superuser=False,
        )

        self.client.force_login(usuario_staff)

        resposta = self.client.get(reverse("admin:index"))

        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, "vagas/aluno/")
        self.assertNotContains(resposta, "vagas/empresa/")
        self.assertNotContains(resposta, "vagas/vaga/")
        self.assertNotContains(resposta, "vagas/candidatura/")

    def test_ADM_04_painel_nao_exibe_detalhes_tecnicos_em_erro(self):
        """ADM-04: página inexistente não revela detalhes técnicos."""
        self.client.force_login(self.admin)

        resposta = self.client.get(
            "/endereco-inexistente-para-teste-adm-04/"
        )

        self.assertEqual(resposta.status_code, 404)
        self.assertNotContains(resposta, "Traceback",                             
        status_code=404,
        )  
        self.assertNotContains(resposta, "SECRET_KEY",
        status_code=404,
        )

    def test_ADM_05_senha_nao_e_exibida_no_painel(self):
        """ADM-05: painel não deve exibir senhas em texto simples."""
        self.client.force_login(self.admin)

        resposta = self.client.get(reverse("admin:index"))

        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, "Empresa@123")

    def test_ADM_06_staff_sem_permissao_nao_altera_curso(self):
        """ADM-06: usuário staff sem permissão não altera cursos."""
        usuario_staff = User.objects.create_user(
            username="staff_sem_permissao_adm06",
            email="staff_adm06@example.com",
            password=self.senha,
            is_staff=True,
            is_superuser=False,
        )

        self.client.force_login(usuario_staff)

        resposta = self.client.get(
            reverse("admin:vagas_curso_changelist")
        )

        self.assertEqual(resposta.status_code, 403)

        resposta_edicao = self.client.get(
            reverse(
                "admin:vagas_curso_change",
                args=[self.curso.pk],
            )
        )

        self.assertEqual(resposta_edicao.status_code, 403)
