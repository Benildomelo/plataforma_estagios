from django.contrib import admin
from django.urls import path
from vagas.views import (
    inicio,
    lista_vagas,
    detalhe_vaga,
    entrar,
    candidatar,
    minhas_candidaturas,
    sair,
    area_aluno,
    area_empresa,
    criar_vaga,
    atualizar_candidatura,
    cadastro_aluno,
    entrar_aluno,
    entrar_empresa, 
    detalhe_vaga_empresa,
    editar_vaga,
    encerrar_vaga,
    perfil_aluno,
    perfil_empresa,
    editar_perfil_aluno,
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', inicio, name='inicio'),

    path('entrar/', entrar, name='entrar'),

    path('cadastro-aluno/', cadastro_aluno, name='cadastro_aluno'),

    path('vagas/', lista_vagas, name='lista_vagas'),

    path(
        'vagas/<int:vaga_id>/',
        detalhe_vaga,
        name='detalhe_vaga'
    ),

    path(
        'vagas/<int:vaga_id>/candidatar/',
        candidatar,
        name='candidatar'
    ),

    path(
        'minhas-candidaturas/',
        minhas_candidaturas,
        name='minhas_candidaturas'
    ),

    path('sair/', sair, name='sair'),

    path(
        'area-aluno/',
        area_aluno,
        name='area_aluno'
    ),

    path(
        'area-empresa/',
        area_empresa,
        name='area_empresa'
    ),

    path(
        'criar-vaga/',
        criar_vaga,
        name='criar_vaga'
    ),

    path(
        'candidaturas/<int:candidatura_id>/atualizar/',
        atualizar_candidatura,
        name='atualizar_candidatura'
    ),

    path(
        'entrar-aluno/', 
        entrar_aluno, name='entrar_aluno'
    ),

    path(
        'entrar-empresa/', 
        entrar_empresa, name='entrar_empresa'
    ),

    path(
        'empresa/vagas/<int:vaga_id>/',
        detalhe_vaga_empresa,
        name='detalhe_vaga_empresa'
    ),

    path(
        'empresa/vagas/<int:vaga_id>/editar/',
        editar_vaga,
        name='editar_vaga'
    ),

    path(
        'empresa/vagas/<int:vaga_id>/encerrar/',
        encerrar_vaga,
        name='encerrar_vaga'
    ),
    path(
        'perfil-aluno/',
        perfil_aluno,
        name='perfil_aluno'
    ),
    path(
        'perfil-aluno/editar/',
        editar_perfil_aluno,
        name='editar_perfil_aluno'
    ),
    path(
        'perfil-empresa/',
        perfil_empresa,
        name='perfil_empresa'
    ),
]