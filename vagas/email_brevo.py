
import os
import requests

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class BrevoEmailBackend(BaseEmailBackend):
    """
    Backend de e-mail do Django usando a API HTTP do Brevo.
    """

    API_URL = "https://api.brevo.com/v3/smtp/email"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = os.getenv("BREVO_API_KEY")

        if not api_key:
            if not self.fail_silently:
                raise ValueError(
                    "A variável BREVO_API_KEY não foi configurada."
                )
            return 0

        enviados = 0

        for message in email_messages:
            remetente = message.from_email or settings.DEFAULT_FROM_EMAIL

            payload = {
                "sender": {
                    "email": remetente,
                },
                "to": [
                    {
                        "email": destinatario,
                    }
                    for destinatario in message.recipients()
                ],
                "subject": message.subject,
                "textContent": message.body,
            }

            # Preserva o conteúdo HTML quando o e-mail possui alternativa HTML.
            alternativas_html = [
                conteudo
                for conteudo, tipo in message.alternatives
                if tipo == "text/html"
            ]

            if alternativas_html:
                payload["htmlContent"] = alternativas_html[0]

            try:
                resposta = requests.post(
                    self.API_URL,
                    headers={
                        "accept": "application/json",
                        "api-key": api_key,
                        "content-type": "application/json",
                    },
                    json=payload,
                    timeout=20,
                )

                resposta.raise_for_status()
                enviados += 1

            except requests.RequestException:
                if not self.fail_silently:
                    raise

        return enviados
