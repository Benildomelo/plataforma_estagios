
import json
from unittest.mock import call, patch

from django.urls import reverse

from .base import BaseTestePlano
from vagas.models import Candidatura


class TestApiCandidatura(BaseTestePlano):

    def setUp(self):
        super().setUp()
        self.url = reverse("api_candidatar")
        self.vaga = self.criar_vaga()

    def enviar(self, dados, content_type="application/json"):
        return self.client.post(
            self.url,
            data=json.dumps(dados),
            content_type=content_type,
        )

    def payload(self, aluno_id=None, vaga_id=None):
        return {
            "aluno_id": (
                aluno_id if aluno_id is not None else self.aluno.id
            ),
            "vaga_id": (
                vaga_id if vaga_id is not None else self.vaga.id
            ),
        }

    def test_API_01_metodo_diferente_de_post_retorna_405(self):
        resposta = self.client.get(self.url)

        self.assertEqual(resposta.status_code, 405)
        self.assertIn("erro", resposta.json())

    def test_API_02_json_invalido_retorna_400(self):
        resposta = self.client.post(
            self.url,
            data="{json inválido",
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())

    def test_API_03_aluno_inexistente_retorna_404(self):
        resposta = self.enviar(
            self.payload(aluno_id=999999)
        )

        self.assertEqual(resposta.status_code, 404)
        self.assertIn("erro", resposta.json())

    def test_API_04_campos_ausentes_retorna_400(self):
        resposta = self.enviar({})

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())

    @patch("vagas.services.candidatura_service.publicar_evento")
    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_API_05_candidatura_valida_retorna_202(
        self,
        mock_validar_vaga,
        mock_publicar_evento,
    ):
        mock_validar_vaga.return_value = {"valida": True}

        with self.captureOnCommitCallbacks(execute=True):
            resposta = self.enviar(self.payload())

        self.assertEqual(resposta.status_code, 202)

        corpo = resposta.json()
        self.assertTrue(corpo["criada"])
        self.assertEqual(
            corpo["candidatura"]["aluno_id"],
            self.aluno.id,
        )
        self.assertEqual(
            corpo["candidatura"]["vaga_id"],
            self.vaga.id,
        )

        self.assertEqual(Candidatura.objects.count(), 1)
        mock_validar_vaga.assert_called_once_with(self.vaga.id)
        mock_publicar_evento.assert_called_once()

    @patch("vagas.services.candidatura_service.publicar_evento")
    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_API_06_candidatura_duplicada_retorna_200(
        self,
        mock_validar_vaga,
        mock_publicar_evento,
    ):
        mock_validar_vaga.return_value = {"valida": True}

        with self.captureOnCommitCallbacks(execute=True):
            primeira = self.enviar(self.payload())
            segunda = self.enviar(self.payload())

        self.assertEqual(primeira.status_code, 202)
        self.assertEqual(segunda.status_code, 200)
        self.assertFalse(segunda.json()["criada"])
        self.assertEqual(Candidatura.objects.count(), 1)
        mock_publicar_evento.assert_called_once()

    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_API_07_vaga_inexistente_retorna_400(
        self,
        mock_validar_vaga,
    ):
        resposta = self.enviar(
            self.payload(vaga_id=999999)
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        mock_validar_vaga.assert_not_called()

    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_API_08_vaga_pendente_retorna_400(
        self,
        mock_validar_vaga,
    ):
        self.vaga.status = "PENDENTE"
        self.vaga.save(update_fields=["status"])

        resposta = self.enviar(self.payload())

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        mock_validar_vaga.assert_not_called()

    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_API_09_vaga_inativa_retorna_400(
        self,
        mock_validar_vaga,
    ):
        self.vaga.ativo = False
        self.vaga.save(update_fields=["ativo"])

        resposta = self.enviar(self.payload())

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        mock_validar_vaga.assert_not_called()

    @patch("vagas.services.candidatura_service.publicar_evento")
    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_API_10_microservico_rejeita_vaga(
        self,
        mock_validar_vaga,
        mock_publicar_evento,
    ):
        mock_validar_vaga.return_value = {"valida": False}

        resposta = self.enviar(self.payload())

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        self.assertEqual(Candidatura.objects.count(), 0)
        mock_publicar_evento.assert_not_called()

    @patch("vagas.services.candidatura_service.publicar_evento")
    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_API_11_microservico_indisponivel(
        self,
        mock_validar_vaga,
        mock_publicar_evento,
    ):
        mock_validar_vaga.side_effect = ValueError(
            "O microserviço está indisponível."
        )

        resposta = self.enviar(self.payload())

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        self.assertEqual(Candidatura.objects.count(), 0)
        mock_publicar_evento.assert_not_called()

    @patch("vagas.services.candidatura_service.publicar_evento")
    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_API_12_resposta_incompleta_do_microservico(
        self,
        mock_validar_vaga,
        mock_publicar_evento,
    ):
        mock_validar_vaga.side_effect = ValueError(
            "O microserviço retornou uma resposta incompleta."
        )

        resposta = self.enviar(self.payload())

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        self.assertEqual(Candidatura.objects.count(), 0)
        mock_publicar_evento.assert_not_called()


    @patch("vagas.services.candidatura_service.publicar_evento")
    @patch("vagas.services.candidatura_service.validar_vaga")
    def test_API_13_consistencia_apos_falha(
        self,
        mock_validar_vaga,
        mock_publicar_evento,
    ):
        # Primeira tentativa: microserviço indisponível.
        mock_validar_vaga.side_effect = [
            ValueError(
                "O microserviço está indisponível."
            ),
            {"valida": True},
        ]

        primeira = self.enviar(self.payload())

        self.assertEqual(primeira.status_code, 400)
        self.assertIn("erro", primeira.json())

        # A falha não pode criar candidatura.
        self.assertEqual(
            Candidatura.objects.count(),
            0,
        )

        mock_publicar_evento.assert_not_called()

        # Segunda tentativa: microserviço volta a funcionar.
        with self.captureOnCommitCallbacks(execute=True):
            segunda = self.enviar(self.payload())

        self.assertEqual(segunda.status_code, 202)

        corpo = segunda.json()

        self.assertTrue(corpo["criada"])

        self.assertEqual(
            corpo["candidatura"]["aluno_id"],
            self.aluno.id,
        )

        self.assertEqual(
            corpo["candidatura"]["vaga_id"],
            self.vaga.id,
        )

        # Deve existir somente uma candidatura.
        self.assertEqual(
            Candidatura.objects.count(),
            1,
        )

        # O serviço de validação foi chamado nas duas tentativas.
        self.assertEqual(
            mock_validar_vaga.call_count,
            2,
        )

        mock_validar_vaga.assert_any_call(
            self.vaga.id
        )

        # O evento só deve ser publicado quando a candidatura
        # realmente for criada.
        mock_publicar_evento.assert_called_once()
