from django.contrib import admin
from .models import Curso, Aluno, Empresa, Vaga, Candidatura
from django.contrib.auth.models import User
from django.utils import timezone

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'matricula', 'email', 'curso', 'ativo')
    list_filter = ('ativo', 'curso')
    search_fields = ('nome', 'matricula', 'email')


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nome_fantasia',
        'razao_social',
        'cnpj',
        'email',
        'ativo',
        'usuario'
    )

    list_filter = ('ativo',)

    search_fields = (
        'nome_fantasia',
        'razao_social',
        'cnpj',
        'email'
    )

    def save_model(self, request, obj, form, change):
        if not change:
            usuario = User.objects.create_user(
                username=obj.email,
                email=obj.email,
                password='Empresa@123'
            )

            obj.usuario = usuario

        super().save_model(request, obj, form, change)


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'titulo',
        'empresa',
        'curso',
        'status',
        'ativo',
        'data_publicacao'
    )

    list_display_links = ('titulo', 'empresa', 'curso')

    list_filter = ('status', 'ativo', 'curso')
    search_fields = (
        'titulo',
        'descricao',
        'empresa__nome_fantasia'
    )

    def save_model(self, request, obj, form, change):
        if obj.status == 'APROVADA' and obj.data_publicacao is None:
            obj.data_publicacao = timezone.now()

        if obj.status != 'APROVADA':
            obj.data_publicacao = None

        super().save_model(request, obj, form, change)   
    

    


@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'aluno',
        'vaga',
        'status',
        'data_candidatura'
    )
    list_filter = ('status',)
    search_fields = (
        'aluno__nome',
        'vaga__titulo',
    )