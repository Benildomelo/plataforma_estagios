"""
Setor 1 do plano: acesso, login e sessão (AUTH-01 a AUTH-09).

Cada teste leva o ID do plano no nome. O docstring traz o resultado esperado
conforme o documento. Se um teste FALHAR, isso indica um defeito no sistema
(a falha deve ser registrada como FA no plano), não um erro do teste.
"""
from django.contrib.sessions.models import Session
from django.test.client import RedirectCycleError
from django.urls import reverse

from vagas.models import Candidatura

from .base import BaseTestePlano

PAGINAS_LOGIN = ["entrar_aluno", "entrar_empresa", "entrar_instituicao"]


def esta_logado(client):
    return "_auth_user_id" in client.session


class TestesAuth(BaseTestePlano):

    # ------------------------------------------------------------------
    # Extra - a tela genérica /entrar/ não deve existir
    # ------------------------------------------------------------------
    def test_AUTH_extra_tela_generica_entrar_foi_removida(self):
        """
        Só existem as telas /entrar-aluno/, /entrar-empresa/ e
        /entrar-instituicao/. A antiga /entrar/ deve responder 404.
        """
        self.assertEqual(self.client.get("/entrar/").status_code, 404)

    # ------------------------------------------------------------------
    # AUTH-01 - Abrir página inicial
    # ------------------------------------------------------------------
    def test_AUTH_01_pagina_inicial_carrega(self):
        """Página carrega sem erro; conteúdo principal e navegação aparecem."""
        resposta = self.client.get(reverse("inicio"))

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "vagas/publicas/inicio.html")
        self.assertContains(resposta, reverse("lista_vagas"))

    # ------------------------------------------------------------------
    # AUTH-02 - Login válido de aluno
    # ------------------------------------------------------------------
    def test_AUTH_02_login_aluno_com_matricula(self):
        """Login concluído e redirecionamento para a área do aluno."""
        resposta = self.client.post(
            reverse("entrar_aluno"),
            {"username": self.aluno.matricula, "password": self.senha},
        )

        self.assertRedirects(resposta, reverse("area_aluno"))
        self.assertTrue(esta_logado(self.client))

    def test_AUTH_02_login_aluno_com_usuario(self):
        """Também deve entrar usando o nome de usuário."""
        resposta = self.client.post(
            reverse("entrar_aluno"),
            {"username": "aluno_teste", "password": self.senha},
        )

        self.assertRedirects(resposta, reverse("area_aluno"))
        self.assertTrue(esta_logado(self.client))

    # ------------------------------------------------------------------
    # AUTH-03 - Senha incorreta
    # ------------------------------------------------------------------
    def test_AUTH_03_senha_incorreta_nas_telas_com_mensagem(self):
        """Acesso negado; mensagem clara; a senha digitada não é exibida."""
        casos = [
            ("entrar_aluno", self.aluno.matricula),
            ("entrar_empresa", self.empresa.email),
            ("entrar_instituicao", "admin_teste"),
        ]
        for nome_url, usuario in casos:
            with self.subTest(tela=nome_url):
                self.client.logout()
                resposta = self.client.post(
                    reverse(nome_url),
                    {"username": usuario, "password": "senha-errada-XYZ"},
                )

                self.assertEqual(resposta.status_code, 200)
                self.assertFalse(esta_logado(self.client))
                self.assertContains(resposta, "inválidos")
                self.assertNotContains(resposta, "senha-errada-XYZ")

    # ------------------------------------------------------------------
    # AUTH-04 - Campos de login vazios
    # ------------------------------------------------------------------
    def test_AUTH_04_envio_vazio_nao_gera_erro_no_servidor(self):
        """Sem preencher os campos: sem erro 500 e sem login."""
        for nome_url in PAGINAS_LOGIN:
            with self.subTest(tela=nome_url):
                resposta = self.client.post(
                    reverse(nome_url),
                    {"username": "", "password": ""},
                )

                self.assertEqual(resposta.status_code, 200)
                self.assertFalse(esta_logado(self.client))

    def test_AUTH_04_formularios_marcam_campos_obrigatorios(self):
        """Validação de obrigatoriedade no navegador (atributo required)."""
        for nome_url in PAGINAS_LOGIN:
            with self.subTest(tela=nome_url):
                html = self.client.get(reverse(nome_url)).content.decode()

                self.assertGreaterEqual(html.count("required"), 2)

    # ------------------------------------------------------------------
    # AUTH-05 - Conta inativa/bloqueada
    # ------------------------------------------------------------------
    def test_AUTH_05_aluno_inativo_bloqueado_na_tela_do_aluno(self):
        """Conta inativa não recebe acesso em /entrar-aluno/."""
        self.aluno.ativo = False
        self.aluno.save()

        resposta = self.client.post(
            reverse("entrar_aluno"),
            {"username": self.aluno.matricula, "password": self.senha},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(esta_logado(self.client))

    def test_AUTH_05_empresa_inativa_bloqueada(self):
        """Empresa inativa não recebe acesso em /entrar-empresa/."""
        self.empresa.ativo = False
        self.empresa.save()

        resposta = self.client.post(
            reverse("entrar_empresa"),
            {"username": self.empresa.email, "password": self.senha},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(esta_logado(self.client))

    def test_AUTH_05_usuario_desativado_no_django_nao_entra(self):
        """User.is_active=False não entra por nenhuma tela de login."""
        self.usuario_aluno.is_active = False
        self.usuario_aluno.save()

        self.client.post(
            reverse("entrar_aluno"),
            {"username": "aluno_teste", "password": self.senha},
        )

        self.assertFalse(esta_logado(self.client))

    def test_AUTH_05_aluno_desativado_com_sessao_aberta_perde_acesso(self):
        """
        Aluno desativado enquanto estava logado não deve continuar
        acessando a área do aluno.
        (No código, 'area_aluno' não confere Aluno.ativo.)
        """
        self.client.force_login(self.usuario_aluno)
        self.aluno.ativo = False
        self.aluno.save()

        resposta = self.client.get(reverse("area_aluno"))

        self.assertNotEqual(resposta.status_code, 200)

    # ------------------------------------------------------------------
    # AUTH-06 - Logout
    # ------------------------------------------------------------------
    def test_AUTH_06_logout_encerra_sessao_e_protege_pagina(self):
        """Sessão encerrada; página protegida volta a exigir login."""
        self.client.force_login(self.usuario_aluno)
        self.assertEqual(
            self.client.get(reverse("area_aluno")).status_code, 200
        )

        resposta = self.client.get(reverse("sair"))

        self.assertRedirects(resposta, reverse("inicio"))
        self.assertFalse(esta_logado(self.client))

        resposta = self.client.get(reverse("area_aluno"))
        self.assertRedirects(resposta, reverse("entrar_aluno"))

    # ------------------------------------------------------------------
    # AUTH-07 - URL protegida sem login
    # ------------------------------------------------------------------
    def test_AUTH_07_urls_protegidas_exigem_login(self):
        """Deslogado, cada URL interna redireciona para a tela de login."""
        aluno = "/entrar-aluno/"
        empresa = "/entrar-empresa/"
        instituicao = "/entrar-instituicao/"

        rotas = [
            ("area_aluno", [], aluno),
            ("minhas_candidaturas", [], aluno),
            ("perfil_aluno", [], aluno),
            ("editar_perfil_aluno", [], aluno),
            ("curriculo_aluno", [], aluno),
            ("trocar_senha_aluno", [], aluno),
            ("area_empresa", [], empresa),
            ("criar_vaga", [], empresa),
            ("perfil_empresa", [], empresa),
            ("trocar_senha_empresa", [], empresa),
            ("detalhe_vaga_empresa", [1], empresa),
            ("editar_vaga", [1], empresa),
            ("encerrar_vaga", [1], empresa),
            ("area_instituicao", [], instituicao),
            ("gerenciar_alunos", [], instituicao),
            ("gerenciar_empresas", [], instituicao),
            ("gerenciar_vagas", [], instituicao),
            ("gerenciar_candidaturas", [], instituicao),
            ("detalhes_vaga_instituicao", [1], instituicao),
        ]

        for nome_url, args, destino in rotas:
            with self.subTest(rota=nome_url):
                resposta = self.client.get(reverse(nome_url, args=args))

                self.assertEqual(resposta.status_code, 302)
                self.assertTrue(
                    resposta.url.startswith(destino),
                    f"{nome_url} redirecionou para {resposta.url}",
                )

    def test_AUTH_07_acoes_da_instituicao_por_post_sem_login(self):
        """Aprovar, rejeitar, encerrar e reabrir sem login são bloqueados."""
        vaga = self.criar_vaga(status="PENDENTE")

        for nome_url in [
            "aprovar_vaga",
            "rejeitar_vaga",
            "encerrar_vaga_instituicao",
            "reabrir_vaga",
        ]:
            with self.subTest(acao=nome_url):
                resposta = self.client.post(
                    reverse(nome_url, args=[vaga.id])
                )

                self.assertEqual(resposta.status_code, 302)
                self.assertTrue(
                    resposta.url.startswith("/entrar-instituicao/")
                )

        vaga.refresh_from_db()
        self.assertEqual(vaga.status, "PENDENTE")

    # ------------------------------------------------------------------
    # AUTH-08 - Sessão expirada
    # ------------------------------------------------------------------
    def test_AUTH_08_sessao_expirada_exige_novo_login(self):
        """
        Simula a expiração apagando a sessão no servidor.
        Página protegida volta ao login e candidatura não é criada.
        """
        vaga = self.criar_vaga()
        self.client.force_login(self.usuario_aluno)
        self.assertEqual(
            self.client.get(reverse("area_aluno")).status_code, 200
        )

        Session.objects.all().delete()

        resposta = self.client.get(reverse("area_aluno"))
        self.assertRedirects(resposta, reverse("entrar_aluno"))

        resposta = self.client.post(reverse("candidatar", args=[vaga.id]))
        self.assertRedirects(resposta, reverse("entrar_aluno"))
        self.assertEqual(Candidatura.objects.count(), 0)

    # ------------------------------------------------------------------
    # AUTH-09 - Menus por perfil
    # ------------------------------------------------------------------
    def _links_do_menu(self, usuario):
        self.client.force_login(usuario)
        html = self.client.get(reverse("inicio")).content.decode()
        self.client.logout()
        return {
            "aluno": reverse("minhas_candidaturas") in html,
            "empresa": reverse("area_empresa") in html,
            "instituicao": reverse("area_instituicao") in html,
        }

    def test_AUTH_09_menu_do_aluno(self):
        """Aluno vê só as opções do aluno."""
        menu = self._links_do_menu(self.usuario_aluno)

        self.assertEqual(
            menu, {"aluno": True, "empresa": False, "instituicao": False}
        )

    def test_AUTH_09_menu_da_empresa(self):
        """Empresa vê só as opções da empresa."""
        menu = self._links_do_menu(self.usuario_empresa)

        self.assertEqual(
            menu, {"aluno": False, "empresa": True, "instituicao": False}
        )

    def test_AUTH_09_menu_da_instituicao(self):
        """Instituição (superusuário) vê só as opções da instituição."""
        menu = self._links_do_menu(self.admin)

        self.assertEqual(
            menu, {"aluno": False, "empresa": False, "instituicao": True}
        )

    def _abrir_seguindo(self, usuario, nome_url):
        self.client.force_login(usuario)
        try:
            return self.client.get(reverse(nome_url), follow=True)
        except RedirectCycleError:
            self.fail(
                f"Loop de redirecionamento ao abrir '{nome_url}' "
                f"como {usuario.username}."
            )

    def test_AUTH_09_aluno_nao_acessa_areas_de_empresa_e_instituicao(self):
        """Aluno é barrado nas áreas de outros perfis."""
        casos = [
            ("area_empresa", "vagas/autenticacao/login_empresa.html",
             "vagas/empresa/area_empresa.html"),
            ("criar_vaga", "vagas/autenticacao/login_empresa.html",
             "vagas/empresa/criar_vaga.html"),
            ("area_instituicao", "vagas/autenticacao/login_instituicao.html",
             "vagas/instituicao/area_instituicao.html"),
            ("gerenciar_vagas", "vagas/autenticacao/login_instituicao.html",
             "vagas/instituicao/gerenciar_vagas.html"),
        ]
        for nome_url, permitido, proibido in casos:
            with self.subTest(rota=nome_url):
                resposta = self._abrir_seguindo(self.usuario_aluno, nome_url)

                self.assertEqual(resposta.status_code, 200)
                self.assertTemplateNotUsed(resposta, proibido)
                self.assertTemplateUsed(resposta, permitido)

    def test_AUTH_09_empresa_nao_acessa_areas_de_instituicao(self):
        """Empresa é barrada na área da instituição."""
        for nome_url in ["area_instituicao", "gerenciar_vagas"]:
            with self.subTest(rota=nome_url):
                resposta = self._abrir_seguindo(
                    self.usuario_empresa, nome_url
                )

                self.assertEqual(resposta.status_code, 200)
                self.assertTemplateUsed(
                    resposta, "vagas/autenticacao/login_instituicao.html"
                )

    def test_AUTH_09_empresa_abrindo_area_do_aluno_nao_entra_em_loop(self):
        """
        Empresa logada que abre a área do aluno deve ser tratada com
        segurança (sem loop e sem ver a área do aluno).
        (No código, area_aluno -> cadastro_aluno -> area_aluno se repete
        para quem não tem perfil de aluno.)
        """
        for nome_url in [
            "area_aluno", "perfil_aluno", "curriculo_aluno",
            "minhas_candidaturas",
        ]:
            with self.subTest(rota=nome_url):
                resposta = self._abrir_seguindo(
                    self.usuario_empresa, nome_url
                )

                self.assertEqual(resposta.status_code, 200)

    def test_AUTH_09_instituicao_abrindo_area_do_aluno_nao_entra_em_loop(self):
        """Superusuário que abre a área do aluno também não pode entrar em loop."""
        for nome_url in ["area_aluno", "perfil_aluno", "minhas_candidaturas"]:
            with self.subTest(rota=nome_url):
                resposta = self._abrir_seguindo(self.admin, nome_url)

                self.assertEqual(resposta.status_code, 200)

