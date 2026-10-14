from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Curso, Aluno, Empresa, Vaga, Candidatura
from .repositories.vaga_repository import VagaRepository
from .services.candidatura_service import CandidaturaService


class TestesCandidatura(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(
            nome="Sistemas de Informação",
            ativo=True,
        )

        self.aluno = Aluno.objects.create(
            nome="Aluno de Teste",
            matricula="TESTE001",
            email="aluno.teste@example.com",
            curso=self.curso,
        )

        self.empresa = Empresa.objects.create(
            razao_social="Empresa de Teste LTDA",
            nome_fantasia="Empresa Teste",
            cnpj="12.345.678/0001-99",
            email="empresa.teste@example.com",
        )

        self.vaga = Vaga.objects.create(
            titulo="Estágio em Desenvolvimento",
            descricao="Vaga utilizada em testes automatizados.",
            carga_horaria="20 horas semanais",
            local="Teresina - PI",
            empresa=self.empresa,
            status="APROVADA",
            ativo=True,
            data_publicacao=timezone.now(),
        )

    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_candidatura_valida_e_criada(self, validar_vaga):
        validar_vaga.return_value = {"valida": True}

        candidatura, criada = CandidaturaService.candidatar(
            self.aluno,
            self.vaga.id,
        )

        self.assertTrue(criada)
        self.assertEqual(candidatura.aluno, self.aluno)
        self.assertEqual(candidatura.vaga, self.vaga)
        self.assertEqual(Candidatura.objects.count(), 1)

    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_nao_duplica_candidatura(self, validar_vaga):
        validar_vaga.return_value = {"valida": True}

        existente = Candidatura.objects.create(
            aluno=self.aluno,
            vaga=self.vaga,
        )

        candidatura, criada = CandidaturaService.candidatar(
            self.aluno,
            self.vaga.id,
        )

        self.assertFalse(criada)
        self.assertEqual(candidatura.id, existente.id)
        self.assertEqual(Candidatura.objects.count(), 1)

    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_vaga_inexistente_e_rejeitada(self, validar_vaga):
        with self.assertRaisesMessage(
            ValueError,
            "Vaga não encontrada.",
        ):
            CandidaturaService.candidatar(self.aluno, 999999)

        validar_vaga.assert_not_called()

    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_vaga_pendente_nao_aceita_candidatura(self, validar_vaga):
        self.vaga.status = "PENDENTE"
        self.vaga.save()

        with self.assertRaisesMessage(
            ValueError,
            "Esta vaga não está disponível para candidatura.",
        ):
            CandidaturaService.candidatar(
                self.aluno,
                self.vaga.id,
            )

        validar_vaga.assert_not_called()

    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_vaga_inativa_nao_aceita_candidatura(self, validar_vaga):
        self.vaga.ativo = False
        self.vaga.save()

        with self.assertRaisesMessage(
            ValueError,
            "Esta vaga está inativa.",
        ):
            CandidaturaService.candidatar(
                self.aluno,
                self.vaga.id,
            )

        validar_vaga.assert_not_called()

    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_microservico_pode_rejeitar_vaga(self, validar_vaga):
        validar_vaga.return_value = {"valida": False}

        with self.assertRaisesMessage(
            ValueError,
            "A vaga foi rejeitada pelo microserviço.",
        ):
            CandidaturaService.candidatar(
                self.aluno,
                self.vaga.id,
            )

        self.assertEqual(Candidatura.objects.count(), 0)

    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_indisponibilidade_do_microservico_e_tratada(
        self,
        validar_vaga,
    ):
        validar_vaga.side_effect = ValueError(
            "O microserviço está indisponível."
        )

        with self.assertRaisesMessage(
            ValueError,
            "O microserviço está indisponível.",
        ):
            CandidaturaService.candidatar(
                self.aluno,
                self.vaga.id,
            )

        self.assertEqual(Candidatura.objects.count(), 0)


class TestesVagas(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(
            nome="Administração",
            ativo=True,
        )

        self.empresa = Empresa.objects.create(
            razao_social="Empresa de Teste LTDA",
            nome_fantasia="Empresa Teste",
            cnpj="98.765.432/0001-10",
            email="empresa.teste@example.com",
        )

    def criar_vaga(self, titulo, status, ativo):
        return Vaga.objects.create(
            titulo=titulo,
            descricao="Descrição de teste.",
            carga_horaria="20 horas semanais",
            local="Teresina - PI",
            empresa=self.empresa,
            status=status,
            ativo=ativo,
        )

    def test_listagem_publica_retorna_apenas_aprovadas_ativas(self):
        aprovada = self.criar_vaga(
            "Vaga publicada",
            "APROVADA",
            True,
        )

        self.criar_vaga("Vaga pendente", "PENDENTE", True)
        self.criar_vaga("Vaga encerrada", "ENCERRADA", False)
        self.criar_vaga("Vaga inativa", "APROVADA", False)

        resultado = VagaRepository.buscar_aprovadas()

        self.assertEqual(list(resultado), [aprovada])

    def test_encerrar_vaga_desativa_e_altera_status(self):
        vaga = self.criar_vaga(
            "Vaga para encerrar",
            "APROVADA",
            True,
        )

        VagaRepository.encerrar(vaga)
        vaga.refresh_from_db()

        self.assertFalse(vaga.ativo)
        self.assertEqual(vaga.status, "ENCERRADA")


class TestesAutenticacao(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(
            nome="Sistemas de Informação",
            ativo=True,
        )

        self.senha = "SenhaTeste123!"

        # Usuário e perfil de aluno
        self.usuario_aluno = User.objects.create_user(
            username="aluno_teste",
            email="aluno@example.com",
            password=self.senha,
        )

        self.aluno = Aluno.objects.create(
            usuario=self.usuario_aluno,
            nome="Aluno de Teste",
            matricula="MATTESTE001",
            email="aluno@example.com",
            curso=self.curso,
            ativo=True,
        )

        # Usuário e perfil de empresa
        self.usuario_empresa = User.objects.create_user(
            username="empresa_teste",
            email="empresa@example.com",
            password=self.senha,
        )

        self.empresa = Empresa.objects.create(
            usuario=self.usuario_empresa,
            razao_social="Empresa Teste LTDA",
            nome_fantasia="Empresa Teste",
            cnpj="12345678000199",
            email="empresa@example.com",
            ativo=True,
        )

        # Usuário comum, sem perfil de aluno ou empresa
        self.usuario_comum = User.objects.create_user(
            username="usuario_comum",
            email="comum@example.com",
            password=self.senha,
        )

        # Administrador da instituição
        self.admin = User.objects.create_superuser(
            username="admin_teste",
            email="admin@example.com",
            password=self.senha,
        )

    def test_aluno_entra_com_matricula(self):
        resposta = self.client.post(
            reverse("entrar_aluno"),
            {
                "username": self.aluno.matricula,
                "password": self.senha,
            },
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(
            "_auth_user_id" in self.client.session
        )

    def test_aluno_inativo_nao_consegue_entrar(self):
        self.aluno.ativo = False
        self.aluno.save()

        resposta = self.client.post(
            reverse("entrar_aluno"),
            {
                "username": self.aluno.matricula,
                "password": self.senha,
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_empresa_entra_com_email(self):
        resposta = self.client.post(
            reverse("entrar_empresa"),
            {
                "username": self.empresa.email,
                "password": self.senha,
            },
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(
            "_auth_user_id" in self.client.session
        )

    def test_empresa_inativa_nao_consegue_entrar(self):
        self.empresa.ativo = False
        self.empresa.save()

        resposta = self.client.post(
            reverse("entrar_empresa"),
            {
                "username": self.empresa.email,
                "password": self.senha,
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_usuario_comum_nao_acessa_area_instituicao(self):
        self.client.force_login(self.usuario_comum)

        resposta = self.client.get(
            reverse("area_instituicao"),
        )

        self.assertIn(resposta.status_code, (302, 403))

    def test_superusuario_acessa_area_instituicao(self):
        self.client.force_login(self.admin)

        resposta = self.client.get(
            reverse("area_instituicao"),
        )

        self.assertEqual(resposta.status_code, 200)



class TestesAcoesInstituicao(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(
            nome="Curso de Teste Instituição",
            ativo=True,
        )

        self.admin = User.objects.create_superuser(
            username="admin_acoes",
            email="admin.acoes@example.com",
            password="SenhaTeste123!",
        )

        self.usuario_empresa = User.objects.create_user(
            username="empresa_acoes",
            email="empresa.acoes@example.com",
            password="SenhaTeste123!",
        )

        self.empresa = Empresa.objects.create(
            usuario=self.usuario_empresa,
            razao_social="Empresa Ações LTDA",
            nome_fantasia="Empresa Ações",
            cnpj="11222333000181",
            email="empresa.acoes@example.com",
        )

        self.vaga = Vaga.objects.create(
            titulo="Estágio de Teste Institucional",
            descricao="Vaga utilizada nos testes da instituição.",
            requisitos="Conhecimentos básicos",
            carga_horaria="20 horas semanais",
            local="Teresina - PI",
            empresa=self.empresa,
            curso=self.curso,
            status="PENDENTE",
            ativo=True,
        )

        self.client.force_login(self.admin)

    def _testar_acao(
        self,
        nome_url,
        status_esperado,
        ativo_esperado,
    ):
        resposta = self.client.post(
            reverse(nome_url, args=[self.vaga.id])
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertRedirects(
            resposta,
            reverse("gerenciar_vagas"),
            fetch_redirect_response=False,
        )

        self.vaga.refresh_from_db()

        self.assertEqual(self.vaga.status, status_esperado)
        self.assertEqual(self.vaga.ativo, ativo_esperado)

    def test_aprovar_vaga(self):
        self._testar_acao(
            "aprovar_vaga",
            "APROVADA",
            True,
        )

    def test_rejeitar_vaga(self):
        self._testar_acao(
            "rejeitar_vaga",
            "REJEITADA",
            False,
        )

    def test_encerrar_vaga(self):
        self._testar_acao(
            "encerrar_vaga_instituicao",
            "ENCERRADA",
            False,
        )

    def test_reabrir_vaga(self):
        self.vaga.status = "ENCERRADA"
        self.vaga.ativo = False
        self.vaga.save()

        self._testar_acao(
            "reabrir_vaga",
            "APROVADA",
            True,
        )

    def test_aprovar_vaga_por_get_nao_altera_status(self):
        resposta = self.client.get(
            reverse("aprovar_vaga", args=[self.vaga.id])
        )

        self.assertEqual(resposta.status_code, 302)

        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, "PENDENTE")
        self.assertTrue(self.vaga.ativo)

    def test_usuario_comum_nao_pode_aprovar_vaga(self):
        usuario = User.objects.create_user(
            username="usuario_sem_permissao",
            password="SenhaTeste123!",
        )

        self.client.force_login(usuario)

        resposta = self.client.post(
            reverse("aprovar_vaga", args=[self.vaga.id])
        )

        self.assertEqual(resposta.status_code, 302)

        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, "PENDENTE")

    def test_empresa_nao_pode_aprovar_vaga(self):
        self.client.force_login(self.usuario_empresa)

        resposta = self.client.post(
            reverse("aprovar_vaga", args=[self.vaga.id])
        )

        self.assertEqual(resposta.status_code, 302)

        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, "PENDENTE")

    def test_aprovar_vaga_inexistente_retorna_404(self):
        resposta = self.client.post(
            reverse("aprovar_vaga", args=[999999])
        )

        self.assertEqual(resposta.status_code, 404)

class TestesSegurancaEmpresa(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(
            nome="Curso Teste Segurança",
            ativo=True,
        )

        self.senha = "SenhaTeste123!"

        self.usuario_empresa1 = User.objects.create_user(
            username="empresa_seguranca1",
            email="seguranca1@example.com",
            password=self.senha,
        )

        self.empresa1 = Empresa.objects.create(
            usuario=self.usuario_empresa1,
            razao_social="Empresa Um LTDA",
            nome_fantasia="Empresa Um",
            cnpj="11111111000111",
            email="seguranca1@example.com",
            ativo=True,
        )

        self.usuario_empresa2 = User.objects.create_user(
            username="empresa_seguranca2",
            email="seguranca2@example.com",
            password=self.senha,
        )

        self.empresa2 = Empresa.objects.create(
            usuario=self.usuario_empresa2,
            razao_social="Empresa Dois LTDA",
            nome_fantasia="Empresa Dois",
            cnpj="22222222000122",
            email="seguranca2@example.com",
            ativo=True,
        )

        self.vaga_empresa1 = Vaga.objects.create(
            titulo="Vaga Privada da Empresa Um",
            descricao="Descrição privada da primeira empresa.",
            requisitos="Conhecimentos básicos",
            carga_horaria="20 horas semanais",
            local="Teresina - PI",
            empresa=self.empresa1,
            curso=self.curso,
            status="APROVADA",
            ativo=True,
        )

    def test_empresa_acessa_propria_area(self):
        self.client.force_login(self.usuario_empresa1)

        resposta = self.client.get(
            reverse("area_empresa")
        )

        self.assertEqual(resposta.status_code, 200)

    def test_empresa_acessa_detalhes_da_propria_vaga(self):
        self.client.force_login(self.usuario_empresa1)

        resposta = self.client.get(
            reverse(
                "detalhe_vaga_empresa",
                args=[self.vaga_empresa1.id],
            )
        )

        self.assertEqual(resposta.status_code, 200)

    def test_empresa_nao_acessa_vaga_de_outra_empresa(self):
        self.client.force_login(self.usuario_empresa2)

        resposta = self.client.get(
            reverse(
                "detalhe_vaga_empresa",
                args=[self.vaga_empresa1.id],
            )
        )

        self.assertRedirects(
            resposta,
            reverse("area_empresa"),
            fetch_redirect_response=False,
        )

    def test_usuario_deslogado_nao_acessa_area_empresa(self):
        resposta = self.client.get(
            reverse("area_empresa")
        )

        self.assertRedirects(
            resposta,
            reverse("entrar_empresa"),
            fetch_redirect_response=False,
        )

    def test_usuario_sem_perfil_empresa_nao_acessa_area(self):
        usuario = User.objects.create_user(
            username="usuario_sem_empresa",
            email="semempresa@example.com",
            password=self.senha,
        )

        self.client.force_login(usuario)

        resposta = self.client.get(
            reverse("area_empresa")
        )

        self.assertRedirects(
            resposta,
            reverse("entrar_empresa"),
            fetch_redirect_response=False,
        )

    def test_empresa_edita_propria_vaga(self):
        self.client.force_login(self.usuario_empresa1)

        resposta = self.client.get(
            reverse(
                "editar_vaga",
                args=[self.vaga_empresa1.id],
            )
        )

        self.assertEqual(resposta.status_code, 200)

    def test_empresa_nao_edita_vaga_de_outra_empresa(self):
        self.client.force_login(self.usuario_empresa2)

        titulo_original = self.vaga_empresa1.titulo

        resposta = self.client.post(
            reverse(
                "editar_vaga",
                args=[self.vaga_empresa1.id],
            ),
            {
                "titulo": "Título alterado indevidamente",
                "descricao": "Tentativa de alteração.",
                "requisitos": "Teste",
                "local": "Teresina - PI",
                "carga_horaria": "20 horas semanais",
                "bolsa": "",
                "cursos": [str(self.curso.id)],
            },
        )

        self.assertRedirects(
            resposta,
            reverse("area_empresa"),
            fetch_redirect_response=False,
        )

        self.vaga_empresa1.refresh_from_db()
        self.assertEqual(
            self.vaga_empresa1.titulo,
            titulo_original,
        )

    def test_empresa_nao_acessa_edicao_de_vaga_inexistente(self):
        self.client.force_login(self.usuario_empresa1)

        resposta = self.client.get(
            reverse("editar_vaga", args=[999999])
        )

        self.assertRedirects(
            resposta,
            reverse("area_empresa"),
            fetch_redirect_response=False,
        )

    def test_empresa_encerrar_propria_vaga(self):
        self.client.force_login(self.usuario_empresa1)

        resposta = self.client.post(
            reverse(
                "encerrar_vaga",
                args=[self.vaga_empresa1.id],
            )
        )

        self.assertRedirects(
            resposta,
            reverse("area_empresa"),
            fetch_redirect_response=False,
        )

        self.vaga_empresa1.refresh_from_db()
        self.assertEqual(self.vaga_empresa1.status, "ENCERRADA")
        self.assertFalse(self.vaga_empresa1.ativo)

    def test_empresa_nao_encerra_vaga_de_outra_empresa(self):
        self.client.force_login(self.usuario_empresa2)

        status_original = self.vaga_empresa1.status
        ativo_original = self.vaga_empresa1.ativo

        resposta = self.client.post(
            reverse(
                "encerrar_vaga",
                args=[self.vaga_empresa1.id],
            )
        )

        self.assertRedirects(
            resposta,
            reverse("area_empresa"),
            fetch_redirect_response=False,
        )

        self.vaga_empresa1.refresh_from_db()
        self.assertEqual(
            self.vaga_empresa1.status,
            status_original,
        )
        self.assertEqual(
            self.vaga_empresa1.ativo,
            ativo_original,
        )