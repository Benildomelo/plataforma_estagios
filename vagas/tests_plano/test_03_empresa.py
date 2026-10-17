from django.contrib.auth.models import User
from django.urls import reverse

from .base import BaseTestePlano
from vagas.models import Empresa, Vaga


class TestEmpresa(BaseTestePlano):

    # ==============================================================
    # EMP-01 - Login de empresa ativa
    # ==============================================================

    def test_EMP_01_login_empresa_ativa(self):
        resposta = self.client.post(
            reverse("entrar_empresa"),
            {
                "username": "empresa_a",
                "password": self.senha,
            },
        )

        self.assertRedirects(
            resposta,
            reverse("area_empresa"),
        )

        self.assertTrue(
            self.client.session.get("_auth_user_id")
        )

    # ==============================================================
    # EMP-02 - Criar vaga válida
    # ==============================================================

    def test_EMP_02_criar_vaga_valida(self):
        self.client.force_login(self.usuario_empresa)

        resposta = self.client.post(
            reverse("criar_vaga"),
            {
                "titulo": "Estágio em Desenvolvimento Python",
                "descricao": "Desenvolvimento de aplicações web.",
                "requisitos": "Python e Django",
                "local": "Teresina",
                "carga_horaria": "20h semanais",
                "bolsa": "1200,00",
                "cursos": [str(self.curso.id)],
            },
        )

        self.assertRedirects(
            resposta,
            reverse(
                "detalhe_vaga_empresa",
                args=[Vaga.objects.latest("id").id],
            ),
        )

        vaga = Vaga.objects.latest("id")

        self.assertEqual(
            vaga.empresa,
            self.empresa,
        )

        self.assertEqual(
            vaga.titulo,
            "Estágio em Desenvolvimento Python",
        )

        self.assertEqual(
            vaga.status,
            "APROVADA",
        )

        self.assertTrue(
            vaga.ativo
        )

        self.assertEqual(
            vaga.cursos.count(),
            1,
        )

        self.assertEqual(
            vaga.cursos.first(),
            self.curso,
        )

    # ==============================================================
    # EMP-03 - Criar vaga com obrigatórios vazios
    # ==============================================================

    def test_EMP_03_criar_vaga_com_obrigatorios_vazios(self):
        self.client.force_login(self.usuario_empresa)

        quantidade_antes = Vaga.objects.count()

        resposta = self.client.post(
            reverse("criar_vaga"),
            {
                "titulo": "",
                "descricao": "",
                "requisitos": "",
                "local": "",
                "carga_horaria": "",
                "bolsa": "",
                "cursos": [],
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertEqual(
            Vaga.objects.count(),
            quantidade_antes,
        )

        mensagens = list(resposta.context["messages"])

        self.assertTrue(
            any(
                "obrigatório" in str(mensagem).lower()
                for mensagem in mensagens
            )
        )

    # ==============================================================
    # EMP-04 - Dados limites/inválidos
    # ==============================================================

    def test_EMP_04_criar_vaga_com_bolsa_invalida(self):
        self.client.force_login(self.usuario_empresa)

        quantidade_antes = Vaga.objects.count()

        resposta = self.client.post(
            reverse("criar_vaga"),
            {
                "titulo": "Estágio com bolsa inválida",
                "descricao": "Descrição de teste.",
                "requisitos": "Python",
                "local": "Teresina",
                "carga_horaria": "20h semanais",
                "bolsa": "valor-invalido",
                "cursos": [str(self.curso.id)],
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertEqual(
            Vaga.objects.count(),
            quantidade_antes,
        )

        mensagens = list(resposta.context["messages"])

        self.assertTrue(
            any(
                "bolsa" in str(mensagem).lower()
                and (
                    "válido" in str(mensagem).lower()
                    or "valido" in str(mensagem).lower()
                )
                for mensagem in mensagens
            )
        )

    def test_EMP_04_titulo_acima_do_limite(self):
        self.client.force_login(self.usuario_empresa)

        titulo = "A" * 201

        quantidade_antes = Vaga.objects.count()

        resposta = self.client.post(
            reverse("criar_vaga"),
            {
                "titulo": titulo,
                "descricao": "Descrição de teste.",
                "requisitos": "Python",
                "local": "Teresina",
                "carga_horaria": "20h semanais",
                "bolsa": "1000",
                "cursos": [str(self.curso.id)],
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertEqual(
            Vaga.objects.count(),
            quantidade_antes,
        )

    # ==============================================================
    # EMP-05 - Editar vaga própria
    # ==============================================================

    def test_EMP_05_editar_vaga_propria(self):
        vaga = self.criar_vaga(
            titulo="Título original",
            descricao="Descrição original",
        )

        self.client.force_login(self.usuario_empresa)

        resposta = self.client.post(
            reverse(
                "editar_vaga",
                args=[vaga.id],
            ),
            {
                "titulo": "Título alterado",
                "descricao": "Descrição alterada.",
                "requisitos": "Python e Django",
                "local": "Teresina",
                "carga_horaria": "30h semanais",
                "bolsa": "1500",
                "cursos": [str(self.curso.id)],
            },
        )

        self.assertRedirects(
            resposta,
            reverse(
                "detalhe_vaga_empresa",
                args=[vaga.id],
            ),
        )

        vaga.refresh_from_db()

        self.assertEqual(
            vaga.titulo,
            "Título alterado",
        )

        self.assertEqual(
            vaga.descricao,
            "Descrição alterada.",
        )

        self.assertEqual(
            vaga.requisitos,
            "Python e Django",
        )

        self.assertEqual(
            vaga.local,
            "Teresina",
        )

        self.assertEqual(
            vaga.carga_horaria,
            "30h semanais",
        )

        self.assertEqual(
            str(vaga.bolsa),
            "1500.00",
        )

        # A edição deve devolver a vaga para análise.
        self.assertEqual(
            vaga.status,
            "PENDENTE",
        )

        self.assertFalse(
            vaga.data_publicacao is not None
        )

    # ==============================================================
    # EMP-06 - Editar vaga de outra empresa
    # ==============================================================

    def test_EMP_06_editar_vaga_de_outra_empresa(self):
        vaga = self.criar_vaga(
            empresa=self.empresa_b,
            titulo="Vaga da Empresa B",
        )

        self.client.force_login(self.usuario_empresa)

        resposta = self.client.post(
            reverse(
                "editar_vaga",
                args=[vaga.id],
            ),
            {
                "titulo": "Tentativa de alteração",
                "descricao": "Tentativa indevida.",
                "requisitos": "Python",
                "local": "Teresina",
                "carga_horaria": "20h semanais",
                "bolsa": "1000",
                "cursos": [str(self.curso.id)],
            },
        )

        self.assertRedirects(
            resposta,
            reverse("area_empresa"),
        )

        vaga.refresh_from_db()

        self.assertEqual(
            vaga.empresa,
            self.empresa_b,
        )

        self.assertEqual(
            vaga.titulo,
            "Vaga da Empresa B",
        )

    # ==============================================================
    # EMP-07 - Encerrar vaga própria
    # ==============================================================

    def test_EMP_07_encerrar_vaga_propria(self):
        vaga = self.criar_vaga(
            empresa=self.empresa,
            status="APROVADA",
            ativo=True,
        )

        self.client.force_login(self.usuario_empresa)

        resposta = self.client.post(
            reverse(
                "encerrar_vaga",
                args=[vaga.id],
            )
        )

        self.assertRedirects(
            resposta,
            reverse("area_empresa"),
        )

        vaga.refresh_from_db()

        self.assertFalse(
            vaga.ativo
        )

        self.assertEqual(
            vaga.status,
            "ENCERRADA",
        )

    # ==============================================================
    # EMP-08 - Encerrar vaga de outra empresa
    # ==============================================================

    def test_EMP_08_encerrar_vaga_de_outra_empresa(self):
        vaga = self.criar_vaga(
            empresa=self.empresa_b,
            status="APROVADA",
            ativo=True,
        )

        self.client.force_login(self.usuario_empresa)

        resposta = self.client.post(
            reverse(
                "encerrar_vaga",
                args=[vaga.id],
            )
        )

        self.assertRedirects(
            resposta,
            reverse("area_empresa"),
        )

        vaga.refresh_from_db()

        self.assertTrue(
            vaga.ativo
        )

        self.assertEqual(
            vaga.status,
            "APROVADA",
        )

    # ==============================================================
    # EMP-09 - Conta empresarial inativa
    # ==============================================================

    def test_EMP_09_login_empresa_inativa(self):
        self.empresa.ativo = False
        self.empresa.save()

        resposta = self.client.post(
            reverse("entrar_empresa"),
            {
                "username": "empresa_a",
                "password": self.senha,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertFalse(
            self.client.session.get("_auth_user_id")
        )

    def test_EMP_09_area_empresa_bloqueada_para_empresa_inativa(self):
        self.empresa.ativo = False
        self.empresa.save()

        self.client.force_login(self.usuario_empresa)

        resposta = self.client.get(
            reverse("area_empresa")
        )

        self.assertRedirects(
            resposta,
            reverse("entrar_empresa"),
        )

    def test_EMP_09_detalhe_vaga_empresa_bloqueado_para_empresa_inativa(self):
        vaga = self.criar_vaga(
            empresa=self.empresa,
        )

        self.empresa.ativo = False
        self.empresa.save()

        self.client.force_login(self.usuario_empresa)

        resposta = self.client.get(
            reverse(
                "detalhe_vaga_empresa",
                args=[vaga.id],
            )
        )

        self.assertRedirects(
            resposta,
            reverse("entrar_empresa"),
        )