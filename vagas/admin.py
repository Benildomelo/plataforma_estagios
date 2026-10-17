
from django.contrib import admin
from django.utils import timezone

from .models import (
    Curso,
    Aluno,
    Empresa,
    Vaga,
    Candidatura,
)

from .repositories.usuario_repository import UsuarioRepository


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome',
        'ativo',
    )

    list_filter = (
        'ativo',
    )

    search_fields = (
        'nome',
    )


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome',
        'matricula',
        'email',
        'curso',
        'ativo',
    )

    list_filter = (
        'ativo',
        'curso',
    )

    search_fields = (
        'nome',
        'matricula',
        'email',
    )


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome_fantasia',
        'razao_social',
        'cnpj',
        'email',
        'ativo',
        'usuario',
    )

    list_filter = (
        'ativo',
    )

    search_fields = (
        'nome_fantasia',
        'razao_social',
        'cnpj',
        'email',
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.usuario_id:
            from django.contrib.auth.models import User
            from django.contrib import messages
            from django.contrib.auth.tokens import default_token_generator
            from django.core.mail import send_mail
            from django.urls import reverse
            from django.utils.encoding import force_bytes
            from django.utils.http import urlsafe_base64_encode
            from django.conf import settings
            import secrets
            import string

            # Verifica se já existe um usuário com este e-mail.
            usuario_existente = User.objects.filter(
                email__iexact=obj.email
            ).first()

            if usuario_existente:
                raise ValueError(
                    'Já existe um usuário com este e-mail. '
                    'Utilize outro e-mail ou verifique o cadastro existente.'
                )

            # O nome de usuário será o e-mail da empresa.
            username = obj.email.strip().lower()

            if User.objects.filter(username__iexact=username).exists():
                raise ValueError(
                    'Já existe um usuário com este nome de usuário.'
                )

            # Gera uma senha aleatória que não será enviada por e-mail.
            caracteres = string.ascii_letters + string.digits + '!@#$%&*'
            senha_aleatoria = ''.join(
                secrets.choice(caracteres) for _ in range(32)
            )

            usuario = User.objects.create_user(
                username=username,
                email=obj.email,
                password=senha_aleatoria,
            )

            obj.usuario = usuario
            obj.senha_provisoria = True

            # Salva a empresa antes de enviar o link.
            super().save_model(request, obj, form, change)

            # Gera um link temporário para definir uma senha.
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)

            caminho = reverse(
                'password_reset_confirm',
                kwargs={
                    'uidb64': uid,
                    'token': token,
                },
            )

            link = request.build_absolute_uri(caminho)

            try:
                enviados = send_mail(
                    subject='Defina sua senha - UNIPI Conecta',
                    message=(
                        f'Olá, {obj.nome_fantasia}!\n\n'
                        'Seu acesso à plataforma UNIPI Conecta foi criado '
                        'pelo administrador.\n\n'
                        'Para definir sua senha, acesse o link abaixo:\n'
                        f'{link}\n\n'
                        'Se você não solicitou este acesso, entre em '
                        'contato com a instituição.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.email],
                    fail_silently=False,
                )

                if enviados:
                    messages.success(
                        request,
                        'Empresa cadastrada. Enviamos um link para '
                        'definição de senha ao e-mail informado.'
                    )
                else:
                    messages.warning(
                        request,
                        'Empresa cadastrada, mas o e-mail não foi enviado. '
                        'Verifique a configuração do Brevo.'
                    )

            except Exception:
                messages.warning(
                    request,
                    'Empresa cadastrada, mas não foi possível enviar o '
                    'e-mail. Verifique a configuração do Brevo e tente '
                    'novamente.'
                )

            return

        super().save_model(request, obj, form, change)


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'titulo',
        'empresa',
        'listar_cursos',
        'status',
        'ativo',
        'data_publicacao',
    )

    list_display_links = (
        'titulo',
        'empresa',
    )

    list_filter = (
        'status',
        'ativo',
        'cursos',
    )

    search_fields = (
        'titulo',
        'descricao',
        'empresa__nome_fantasia',
        'cursos__nome',
    )

    @admin.display(description='Cursos')
    def listar_cursos(self, obj):
        return ', '.join(
            curso.nome for curso in obj.cursos.all()
        )

    def save_model(self, request, obj, form, change):
        if (
            obj.status == 'APROVADA'
            and obj.data_publicacao is None
        ):
            obj.data_publicacao = timezone.now()

        if obj.status != 'APROVADA':
            obj.data_publicacao = None

        super().save_model(
            request,
            obj,
            form,
            change,
        )


@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'aluno',
        'vaga',
        'status',
        'data_candidatura',
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'aluno__nome',
        'vaga__titulo',
    )
