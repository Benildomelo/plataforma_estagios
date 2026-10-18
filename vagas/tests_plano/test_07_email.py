
from unittest.mock import patch

import requests

from django.core import mail
from django.test import TestCase, override_settings

from vagas.email_brevo import BrevoEmailBackend


@override_settings(
    DEFAULT_FROM_EMAIL="sistema@teste.com"
)
class TestEmailBrevo(TestCase):

    @patch("vagas.email_brevo.requests.post")
    def test_MAIL_01_envio_de_email_de_fluxo_previsto(
        self,
        mock_post,
    ):
        mock_post.return_value.raise_for_status.return_value = None

        mensagem = mail.EmailMessage(
            subject="Teste de notificação",
            body="Mensagem de teste do sistema.",
            from_email="sistema@teste.com",
            to=["destinatario@teste.com"],
        )

        backend = BrevoEmailBackend()

        enviados = backend.send_messages([mensagem])

        self.assertEqual(enviados, 1)
        mock_post.assert_called_once()

        chamada = mock_post.call_args

        self.assertEqual(
            chamada.kwargs["headers"]["content-type"],
            "application/json",
        )

        self.assertEqual(
            chamada.kwargs["json"]["sender"]["email"],
            "sistema@teste.com",
        )

        self.assertEqual(
            chamada.kwargs["json"]["to"][0]["email"],
            "destinatario@teste.com",
        )

        self.assertEqual(
            chamada.kwargs["json"]["subject"],
            "Teste de notificação",
        )

        self.assertEqual(
            chamada.kwargs["json"]["textContent"],
            "Mensagem de teste do sistema.",
        )

    @patch("vagas.email_brevo.requests.post")
    def test_MAIL_02_destinatario_invalido_trata_falha(
        self,
        mock_post,
    ):
        mock_post.side_effect = Exception(
            "Falha simulada no provedor."
        )

        mensagem = mail.EmailMessage(
            subject="Teste de destinatário inválido",
            body="Mensagem de teste.",
            from_email="sistema@teste.com",
            to=["destinatario-invalido"],
        )

        backend = BrevoEmailBackend()

        with self.assertRaises(Exception):
            backend.send_messages([mensagem])

        mock_post.assert_called_once()


    @patch("vagas.email_brevo.requests.post")
    def test_MAIL_03_provedor_indisponivel_trata_falha(
        self,
        mock_post,
    ):
        mock_post.side_effect = requests.RequestException(
            "Provedor indisponível."
        )

        mensagem = mail.EmailMessage(
            subject="Teste de indisponibilidade",
            body="Mensagem de teste.",
            from_email="sistema@teste.com",
            to=["destinatario@teste.com"],
        )

        backend = BrevoEmailBackend()

        with self.assertRaises(requests.RequestException):
            backend.send_messages([mensagem])

        mock_post.assert_called_once()


    @patch("vagas.email_brevo.requests.post")
    def test_MAIL_04_conteudo_e_links(
        self,
        mock_post,
    ):
        mock_post.return_value.raise_for_status.return_value = None

        mensagem = mail.EmailMultiAlternatives(
            subject="Candidatura recebida",
            body=(
                "Sua candidatura foi registrada com sucesso.\n"
                "Acesse a plataforma para acompanhar."
            ),
            from_email="sistema@teste.com",
            to=["aluno@teste.com"],
        )

        mensagem.attach_alternative(
            """
            <html>
                <body>
                    <p>Sua candidatura foi registrada com sucesso.</p>
                    <p>
                        <a href="https://teste.com/candidaturas">
                            Acompanhar candidatura
                        </a>
                    </p>
                </body>
            </html>
            """,
            "text/html",
        )

        backend = BrevoEmailBackend()

        enviados = backend.send_messages([mensagem])

        self.assertEqual(enviados, 1)
        mock_post.assert_called_once()

        payload = mock_post.call_args.kwargs["json"]

        self.assertEqual(
            payload["subject"],
            "Candidatura recebida",
        )

        self.assertIn(
            "Sua candidatura foi registrada com sucesso.",
            payload["textContent"],
        )

        self.assertIn(
            "Acompanhar candidatura",
            payload["htmlContent"],
        )

        self.assertIn(
            "https://teste.com/candidaturas",
            payload["htmlContent"],
        )

        self.assertNotIn(
            "senha",
            payload["textContent"].lower(),
        )

        self.assertNotIn(
            "token",
            payload["textContent"].lower(),
        )


    @patch("vagas.email_brevo.requests.post")
    def test_MAIL_05_segredos_nao_aparecem_em_mensagens(
        self,
        mock_post,
    ):
        mock_post.return_value.raise_for_status.return_value = None

        mensagem = mail.EmailMessage(
            subject="Notificação de candidatura",
            body=(
                "Sua candidatura foi registrada com sucesso. "
                "Acesse a plataforma para acompanhar o processo."
            ),
            from_email="sistema@teste.com",
            to=["aluno@teste.com"],
        )

        backend = BrevoEmailBackend()

        enviados = backend.send_messages([mensagem])

        self.assertEqual(enviados, 1)
        mock_post.assert_called_once()

        payload = mock_post.call_args.kwargs["json"]

        conteudo = (
            payload["subject"]
            + " "
            + payload["textContent"]
        ).lower()

        self.assertNotIn("senha", conteudo)
        self.assertNotIn("password", conteudo)
        self.assertNotIn("token", conteudo)
        self.assertNotIn("api-key", conteudo)
        self.assertNotIn("apikey", conteudo)
        self.assertNotIn("credencial", conteudo)
        self.assertNotIn("credential", conteudo)

