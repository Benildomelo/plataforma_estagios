
from django.urls import reverse

from vagas.models import Vaga
from vagas.tests_plano.base import BaseTestePlano


class TestesInstituicao(BaseTestePlano):
    """Testes do setor institucional e do gerenciamento de vagas."""

    def setUp(self):
        super().setUp()
        self.vaga = self.criar_vaga(
            status="PENDENTE",
            ativo=True,
        )

    def acessar_como_admin(self):
        self.client.force_login(self.admin)

    def acessar_rota(self, nome_rota, **kwargs):
        return self.client.get(reverse(nome_rota, kwargs=kwargs))

    # INST-01: instituição acessa o painel institucional
    def test_INST01_admin_acessa_painel_institucional(self):
        self.acessar_como_admin()

        resposta = self.acessar_rota("area_instituicao")

        self.assertEqual(resposta.status_code, 200)

    # INST-02: usuário comum não pode aprovar vaga
    def test_INST02_usuario_comum_nao_aprova_vaga(self):
        self.client.force_login(self.usuario_comum)

        resposta = self.client.post(
            reverse("aprovar_vaga", kwargs={"vaga_id": self.vaga.id})
        )

        self.vaga.refresh_from_db()

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(self.vaga.status, "PENDENTE")
        self.assertTrue(self.vaga.ativo)

    # INST-03: empresa não pode aprovar a própria vaga
    def test_INST03_empresa_nao_aprova_propria_vaga(self):
        self.client.force_login(self.usuario_empresa)

        resposta = self.client.post(
            reverse("aprovar_vaga", kwargs={"vaga_id": self.vaga.id})
        )

        self.vaga.refresh_from_db()

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(self.vaga.status, "PENDENTE")
        self.assertTrue(self.vaga.ativo)

    # INST-04: instituição aprova vaga pendente
    def test_INST04_admin_aprova_vaga_pendente(self):
        self.acessar_como_admin()

        resposta = self.client.post(
            reverse("aprovar_vaga", kwargs={"vaga_id": self.vaga.id})
        )

        self.vaga.refresh_from_db()

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.url, reverse("gerenciar_vagas"))
        self.assertEqual(self.vaga.status, "APROVADA")
        self.assertTrue(self.vaga.ativo)

    # INST-05: instituição rejeita vaga pendente
    def test_INST05_admin_rejeita_vaga_pendente(self):
        self.acessar_como_admin()

        resposta = self.client.post(
            reverse("rejeitar_vaga", kwargs={"vaga_id": self.vaga.id})
        )

        self.vaga.refresh_from_db()

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.url, reverse("gerenciar_vagas"))
        self.assertEqual(self.vaga.status, "REJEITADA")
        self.assertFalse(self.vaga.ativo)

    # INST-06: instituição encerra vaga aprovada
    def test_INST06_admin_encerra_vaga_aprovada(self):
        self.vaga.status = "APROVADA"
        self.vaga.ativo = True
        self.vaga.save(update_fields=["status", "ativo"])

        self.acessar_como_admin()

        resposta = self.client.post(
            reverse(
                "encerrar_vaga_instituicao",
                kwargs={"vaga_id": self.vaga.id},
            )
        )

        self.vaga.refresh_from_db()

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(self.vaga.status, "ENCERRADA")
        self.assertFalse(self.vaga.ativo)

    # INST-07: instituição reabre vaga encerrada
    def test_INST07_admin_reabre_vaga_encerrada(self):
        self.vaga.status = "ENCERRADA"
        self.vaga.ativo = False
        self.vaga.save(update_fields=["status", "ativo"])

        self.acessar_como_admin()

        resposta = self.client.post(
            reverse("reabrir_vaga", kwargs={"vaga_id": self.vaga.id})
        )

        self.vaga.refresh_from_db()

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(self.vaga.status, "APROVADA")
        self.assertTrue(self.vaga.ativo)

    # INST-08: tentativa de operar sobre vaga inexistente
    def test_INST08_vaga_inexistente_retorna_404(self):
        self.acessar_como_admin()

        id_inexistente = 999999

        with self.assertRaises(Vaga.DoesNotExist):
            Vaga.objects.get(id=id_inexistente)

        resposta = self.client.post(
            reverse("aprovar_vaga", kwargs={"vaga_id": id_inexistente})
        )

        self.assertEqual(resposta.status_code, 404)

    # INST-09: consistência entre status e ativo
    def test_INST09_status_e_ativo_ficam_consistentes(self):
        self.acessar_como_admin()

        acoes = [
            ("aprovar_vaga", "APROVADA", True),
            ("rejeitar_vaga", "REJEITADA", False),
            ("encerrar_vaga_instituicao", "ENCERRADA", False),
            ("reabrir_vaga", "APROVADA", True),
        ]

        for nome_rota, status_esperado, ativo_esperado in acoes:
            with self.subTest(rota=nome_rota):
                self.vaga.status = "PENDENTE"
                self.vaga.ativo = True
                self.vaga.save(update_fields=["status", "ativo"])

                resposta = self.client.post(
                    reverse(nome_rota, kwargs={"vaga_id": self.vaga.id})
                )

                self.assertEqual(resposta.status_code, 302)

                self.vaga.refresh_from_db()

                self.assertEqual(self.vaga.status, status_esperado)
                self.assertEqual(self.vaga.ativo, ativo_esperado)

    # INST-10: usuário autenticado sem perfil institucional não acessa o painel
    def test_INST10_usuario_comum_nao_acessa_rotas_institucionais(self):
        self.client.force_login(self.usuario_comum)

        rotas = [
            ("area_instituicao", {}),
            ("gerenciar_vagas", {}),
            ("detalhes_vaga_instituicao", {"vaga_id": self.vaga.id}),
        ]

        for nome_rota, kwargs in rotas:
            with self.subTest(rota=nome_rota):
                resposta = self.client.get(reverse(nome_rota, kwargs=kwargs))
                self.assertEqual(resposta.status_code, 302)

    # Ações institucionais devem exigir POST
    def test_acoes_institucionais_nao_alteram_vaga_por_get(self):
        self.acessar_como_admin()

        acoes = [
            "aprovar_vaga",
            "rejeitar_vaga",
            "encerrar_vaga_instituicao",
            "reabrir_vaga",
        ]

        for nome_rota in acoes:
            with self.subTest(rota=nome_rota):
                self.vaga.status = "PENDENTE"
                self.vaga.ativo = True
                self.vaga.save(update_fields=["status", "ativo"])

                resposta = self.client.get(
                    reverse(nome_rota, kwargs={"vaga_id": self.vaga.id})
                )

                self.assertEqual(resposta.status_code, 302)

                self.vaga.refresh_from_db()
                self.assertEqual(self.vaga.status, "PENDENTE")
                self.assertTrue(self.vaga.ativo)
