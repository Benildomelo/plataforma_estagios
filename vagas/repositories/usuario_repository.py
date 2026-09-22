from django.contrib.auth.models import User


class UsuarioRepository:

    @staticmethod
    def buscar_por_username(username):
        return User.objects.filter(
            username=username
        ).first()

    @staticmethod
    def buscar_por_email(email):
        return User.objects.filter(
            email=email
        ).first()

    @staticmethod
    def criar(username, email, password):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password
        )