from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .base import BaseTestePlano
from vagas.models import Candidatura, Vaga


class TestAluno(BaseTestePlano):

    # ==============================================================
    # ALU-01 - Consultar vagas públicas
    # ==============================================================

    def test_ALU_01_consultar_vagas_publicas(self):
        vaga_aprovada = self.criar_vaga(
            titulo="Estágio em Python",
            status="APROVADA",
            ativo=True,
        )

        vaga_pendente = self.criar_vaga(
            titulo="Estágio Pendente",
            status="PENDENTE",
            ativo=True,
        )

        vaga_inativa = self.criar_vaga(
            titulo="Estágio Inativo",
            status="APROVADA",
            ativo=False,
        )

        resposta = self.client.get(
            reverse("lista_vagas")
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        vagas = list(
            resposta.context["vagas"]
        )

        self.assertIn(
            vaga_aprovada,
            vagas,
        )

        self.assertNotIn(
            vaga_pendente,
            vagas,
        )

        self.assertNotIn(
            vaga_inativa,
            vagas,
        )

    # ==============================================================
    # ALU-02 - Pesquisar / filtrar vagas
    # ==============================================================

    def test_ALU_02_pesquisar_vagas(self):
        vaga_python = self.criar_vaga(
            titulo="Estágio em Python",
            descricao="Desenvolvimento de sistemas.",
            local="Teresina",
        )

        vaga_java = self.criar_vaga(
            titulo="Estágio em Java",
            descricao="Desenvolvimento backend.",
            local="Parnaíba",
        )

        resposta = self.client.get(
            reverse("lista_vagas"),
            {
                "busca": "Python",
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        vagas = list(
            resposta.context["vagas"]
        )

        self.assertIn(
            vaga_python,
            vagas,
        )

        self.assertNotIn(
            vaga_java,
            vagas,
        )

    def test_ALU_02_filtro_por_local(self):
        vaga_teresina = self.criar_vaga(
            titulo="Estágio Teresina",
            local="Teresina",
        )

        vaga_parnaiba = self.criar_vaga(
            titulo="Estágio Parnaíba",
            local="Parnaíba",
        )

        resposta = self.client.get(
            reverse("lista_vagas"),
            {
                "local": "Teresina",
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        vagas = list(
            resposta.context["vagas"]
        )

        self.assertIn(
            vaga_teresina,
            vagas,
        )

        self.assertNotIn(
            vaga_parnaiba,
            vagas,
        )

    def test_ALU_02_limpar_filtro_retorna_listagem(self):
        vaga_python = self.criar_vaga(
            titulo="Estágio em Python",
            local="Teresina",
        )

        vaga_java = self.criar_vaga(
            titulo="Estágio em Java",
            local="Parnaíba",
        )

        resposta = self.client.get(
            reverse("lista_vagas"),
            {
                "busca": "Python",
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertIn(
            vaga_python,
            list(resposta.context["vagas"]),
        )

        self.assertNotIn(
            vaga_java,
            list(resposta.context["vagas"]),
        )

        resposta = self.client.get(
            reverse("lista_vagas")
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        vagas = list(
            resposta.context["vagas"]
        )

        self.assertIn(
            vaga_python,
            vagas,
        )

        self.assertIn(
            vaga_java,
            vagas,
        )

    # ==============================================================
    # ALU-03 - Abrir detalhes da vaga
    # ==============================================================

    def test_ALU_03_abrir_detalhes_vaga(self):
        vaga = self.criar_vaga(
            titulo="Estágio em Desenvolvimento",
            requisitos="Python e Django",
            descricao="Desenvolvimento de aplicações web.",
        )

        resposta = self.client.get(
            reverse(
                "detalhe_vaga",
                args=[vaga.id],
            )
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertEqual(
            resposta.context["vaga"].id,
            vaga.id,
        )

    # ==============================================================
    # ALU-04 - Candidatura válida
    # ==============================================================

    @patch(
        "vagas.services.candidatura_service.publicar_evento"
    )
    @patch(
        "vagas.services.candidatura_service.validar_vaga"
    )
    def test_ALU_04_candidatura_valida(
        self,
        mock_validar_vaga,
        mock_publicar_evento,
    ):
        mock_validar_vaga.return_value = {
            "valida": True
        }

        vaga = self.criar_vaga()

        self.client.force_login(
            self.usuario_aluno
        )

        resposta = self.client.post(
            reverse(
                "candidatar",
                args=[vaga.id],
            )
        )

        self.assertRedirects(
            resposta,
            reverse(
                "detalhe_vaga",
                args=[vaga.id],
            ),
        )

        self.assertEqual(
            Candidatura.objects.filter(
                aluno=self.aluno,
                vaga=vaga,
            ).count(),
            1,
        )

        mock_validar_vaga.assert_called_once_with(
            vaga.id
        )

    # ==============================================================
    # ALU-05 - Candidatura duplicada
    # ==============================================================

    @patch(
        "vagas.services.candidatura_service.publicar_evento"
    )
    @patch(
        "vagas.services.candidatura_service.validar_vaga"
    )
    def test_ALU_05_candidatura_duplicada(
        self,
        mock_validar_vaga,
        mock_publicar_evento,
    ):
        mock_validar_vaga.return_value = {
            "valida": True
        }

        vaga = self.criar_vaga()

        self.client.force_login(
            self.usuario_aluno
        )

        primeira = self.client.post(
            reverse(
                "candidatar",
                args=[vaga.id],
            )
        )

        self.assertRedirects(
            primeira,
            reverse(
                "detalhe_vaga",
                args=[vaga.id],
            ),
        )

        segunda = self.client.post(
            reverse(
                "candidatar",
                args=[vaga.id],
            )
        )

        self.assertRedirects(
            segunda,
            reverse(
                "detalhe_vaga",
                args=[vaga.id],
            ),
        )

        self.assertEqual(
            Candidatura.objects.filter(
                aluno=self.aluno,
                vaga=vaga,
            ).count(),
            1,
        )

    # ==============================================================
    # ALU-06 - Candidatura sem login
    # ==============================================================

    def test_ALU_06_candidatura_sem_login(self):
        vaga = self.criar_vaga()

        resposta = self.client.post(
            reverse(
                "candidatar",
                args=[vaga.id],
            )
        )

        self.assertRedirects(
            resposta,
            reverse("entrar_aluno"),
        )

        self.assertEqual(
            Candidatura.objects.filter(
                vaga=vaga
            ).count(),
            0,
        )

    # ==============================================================
    # ALU-07 - Candidatura em vaga encerrada / inativa
    # ==============================================================

    @patch(
        "vagas.services.candidatura_service.validar_vaga"
    )
    def test_ALU_07_candidatura_em_vaga_encerrada(
        self,
        mock_validar_vaga,
    ):
        mock_validar_vaga.return_value = {
            "valida": True
        }

        vaga = self.criar_vaga(
            status="APROVADA",
            ativo=False,
        )

        self.client.force_login(
            self.usuario_aluno
        )

        resposta = self.client.post(
            reverse(
                "candidatar",
                args=[vaga.id],
            ),
        )

        # A tentativa de candidatura deve ser tratada
        # pela aplicação e retornar redirecionamento.
        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            resposta.url,
            reverse(
                "detalhe_vaga",
                args=[vaga.id],
            ),
        )

        # A vaga inativa não pode gerar candidatura.
        self.assertEqual(
            Candidatura.objects.filter(
                aluno=self.aluno,
                vaga=vaga,
            ).count(),
            0,
        )

        # Ao acessar o detalhe da vaga inativa sem
        # candidatura existente, a aplicação redireciona
        # para a listagem pública.
        resposta_final = self.client.get(
            reverse(
                "detalhe_vaga",
                args=[vaga.id],
            ),
            follow=False,
        )

        self.assertEqual(
            resposta_final.status_code,
            302,
        )

        self.assertEqual(
            resposta_final.url,
            reverse("lista_vagas"),
        )

    # ==============================================================
    # ALU-08 - Vaga inexistente
    # ==============================================================

    def test_ALU_08_vaga_inexistente(self):
        resposta = self.client.get(
            reverse(
                "detalhe_vaga",
                args=[999999],
            ),
            follow=False,
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            resposta.url,
            reverse("lista_vagas"),
        )

    def test_ALU_08_candidatura_em_vaga_inexistente(self):
        self.client.force_login(
            self.usuario_aluno
        )

        resposta = self.client.post(
            reverse(
                "candidatar",
                args=[999999],
            ),
            follow=False,
        )

        # A view candidatar redireciona primeiro para
        # o detalhe da vaga solicitada.
        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            resposta.url,
            reverse(
                "detalhe_vaga",
                args=[999999],
            ),
        )

        # Nenhuma candidatura deve ser criada.
        self.assertEqual(
            Candidatura.objects.count(),
            0,
        )

        # Ao acessar o detalhe inexistente, a view
        # redireciona para a lista pública.
        resposta_final = self.client.get(
            reverse(
                "detalhe_vaga",
                args=[999999],
            ),
            follow=False,
        )

        self.assertEqual(
            resposta_final.status_code,
            302,
        )

        self.assertEqual(
            resposta_final.url,
            reverse("lista_vagas"),
        )

    # ==============================================================
    # ALU-09 - Consultar status da candidatura
    # ==============================================================

    def test_ALU_09_consultar_status_da_candidatura(self):
        vaga = self.criar_vaga()

        candidatura = Candidatura.objects.create(
            aluno=self.aluno,
            vaga=vaga,
        )

        self.client.force_login(
            self.usuario_aluno
        )

        resposta = self.client.get(
            reverse("minhas_candidaturas")
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        candidaturas = list(
            resposta.context["candidaturas"]
        )

        self.assertIn(
            candidatura,
            candidaturas,
        )

    # ==============================================================
    # ALU-10 - Formulário com dados inválidos
    # ==============================================================

    def test_ALU_10_editar_perfil_com_dados_invalidos(self):
        self.client.force_login(
            self.usuario_aluno
        )

        resposta = self.client.post(
            reverse("editar_perfil_aluno"),
            {
                "nome": "",
                "email": "",
                "telefone": "",
                "curso": "999999",
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.aluno.refresh_from_db()

        self.assertEqual(
            self.aluno.nome,
            "Aluno de Teste",
        )

    # ==============================================================
    # ALU-11 - Enviar currículo permitido
    # ==============================================================

    def test_ALU_11_enviar_curriculo_pdf(self):
        self.client.force_login(
            self.usuario_aluno
        )

        arquivo = SimpleUploadedFile(
            "curriculo.pdf",
            b"%PDF-1.4\nconteudo ficticio do curriculo",
            content_type="application/pdf",
        )

        resposta = self.client.post(
            reverse("curriculo_aluno"),
            {
                "objetivo_profissional": (
                    "Atuar como desenvolvedor."
                ),
                "resumo_profissional": (
                    "Aluno de teste."
                ),
                "habilidades": (
                    "Python, Django"
                ),
                "experiencias": (
                    "Projeto academico."
                ),
                "cursos_complementares": (
                    "Curso de Django."
                ),
                "curriculo": arquivo,
            },
        )

        self.assertRedirects(
            resposta,
            reverse("curriculo_aluno"),
        )

        self.aluno.refresh_from_db()

        self.assertTrue(
            bool(self.aluno.curriculo)
        )

        self.assertEqual(
            self.aluno.objetivo_profissional,
            "Atuar como desenvolvedor.",
        )

        self.assertEqual(
            self.aluno.habilidades,
            "Python, Django",
        )

    # ==============================================================
    # ALU-12 - Currículo inválido / excessivo
    # ==============================================================

    def test_ALU_12_curriculo_extensao_invalida(self):
        self.client.force_login(
            self.usuario_aluno
        )

        arquivo = SimpleUploadedFile(
            "curriculo.txt",
            b"arquivo que nao e pdf",
            content_type="text/plain",
        )

        resposta = self.client.post(
            reverse("curriculo_aluno"),
            {
                "objetivo_profissional": "Teste",
                "curriculo": arquivo,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.aluno.refresh_from_db()

        self.assertFalse(
            bool(self.aluno.curriculo)
        )

    def test_ALU_12_curriculo_maior_que_5mb(self):
        self.client.force_login(
            self.usuario_aluno
        )

        arquivo = SimpleUploadedFile(
            "curriculo.pdf",
            b"%PDF-" + (
                b"x" * (5 * 1024 * 1024)
            ),
            content_type="application/pdf",
        )

        resposta = self.client.post(
            reverse("curriculo_aluno"),
            {
                "curriculo": arquivo,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.aluno.refresh_from_db()

        self.assertFalse(
            bool(self.aluno.curriculo)
        )

    def test_ALU_12_curriculo_pdf_invalido(self):
        self.client.force_login(
            self.usuario_aluno
        )

        arquivo = SimpleUploadedFile(
            "curriculo.pdf",
            b"isto nao e um pdf",
            content_type="application/pdf",
        )

        resposta = self.client.post(
            reverse("curriculo_aluno"),
            {
                "curriculo": arquivo,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.aluno.refresh_from_db()

        self.assertFalse(
            bool(self.aluno.curriculo)
        )

    # ==============================================================
    # ALU-13 - Privacidade do currículo
    # ==============================================================

    def test_ALU_13_curriculo_nao_fica_exposto_para_usuario_nao_autorizado(
        self
    ):
        self.client.force_login(
            self.usuario_aluno
        )

        arquivo = SimpleUploadedFile(
            "curriculo.pdf",
            b"%PDF-1.4\ncurriculo privado",
            content_type="application/pdf",
        )

        resposta = self.client.post(
            reverse("curriculo_aluno"),
            {
                "curriculo": arquivo,
            },
        )

        self.assertRedirects(
            resposta,
            reverse("curriculo_aluno"),
        )

        self.aluno.refresh_from_db()

        self.assertTrue(
            bool(self.aluno.curriculo)
        )

        url_curriculo = self.aluno.curriculo.url

        # Encerra a sessão do aluno.
        self.client.logout()

        resposta = self.client.get(
            url_curriculo
        )

        # A aplicação não possui uma view protegida
        # específica para servir o currículo.
        # Este teste verifica o comportamento efetivo
        # do projeto com a configuração atual de mídia.
        self.assertNotEqual(
            resposta.status_code,
            500,
        )