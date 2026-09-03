from django.contrib import admin

from .models import Curso, Aluno, Empresa, Vaga, Candidatura


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'matricula', 'email', 'curso', 'ativo')
    list_filter = ('curso', 'ativo')
    search_fields = ('nome', 'matricula', 'email')


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome_fantasia',
        'razao_social',
        'cnpj',
        'email',
        'ativo'
    )
    list_filter = ('ativo',)
    search_fields = (
        'nome_fantasia',
        'razao_social',
        'cnpj',
        'email'
    )


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
    list_filter = ('status', 'ativo', 'curso')
    search_fields = (
        'titulo',
        'descricao',
        'empresa__nome_fantasia'
    )


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
        'aluno__matricula',
        'vaga__titulo'
    )