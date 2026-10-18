"""
Configuração usada SOMENTE nos testes do plano (Plano_de_Testes_UNIPI_Conecta).

- Usa SQLite em memória: não conecta no MySQL/Aiven e não toca em dados reais.
- Salva uploads em uma pasta temporária, não em /media do projeto.
- Guarda e-mails em memória: nada é enviado de verdade.

Como rodar:
    python manage.py test vagas.tests_plano --settings=config.settings_test
"""
import tempfile

from .settings import *  # noqa: F401,F403

SECRET_KEY = "chave-somente-para-testes"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

MEDIA_ROOT = tempfile.mkdtemp(prefix="unipi_testes_media_")

VALIDAR_VAGA_MICROSERVICO = True