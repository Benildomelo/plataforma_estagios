from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

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
    cadastro_aluno,
    entrar_aluno,
    entrar_empresa,
    entrar_instituicao,
    detalhe_vaga_empresa,
    editar_vaga,
    encerrar_vaga,
    perfil_aluno,
    perfil_empresa,
    editar_perfil_aluno,
    curriculo_aluno,
    trocar_senha_empresa,
)

from vagas.views.instituicao import (
    area_instituicao,
    gerenciar_alunos,
    gerenciar_empresas,
    gerenciar_vagas,
    gerenciar_candidaturas,
    aprovar_vaga,
    rejeitar_vaga,
    encerrar_vaga_instituicao,
    reabrir_vaga,
)


urlpatterns = [

    # =====================================================
    # ADMIN DJANGO
    # =====================================================

    path(
        'admin/',
        admin.site.urls
    ),


    # =====================================================
    # INÍCIO
    # =====================================================

    path(
        '',
        inicio,
        name='inicio'
    ),


    # =====================================================
    # AUTENTICAÇÃO
    # =====================================================

    path(
        'entrar/',
        entrar,
        name='entrar'
    ),

    path(
        'entrar-aluno/',
        entrar_aluno,
        name='entrar_aluno'
    ),

    path(
        'entrar-empresa/',
        entrar_empresa,
        name='entrar_empresa'
    ),

    path(
        'entrar-instituicao/',
        entrar_instituicao,
        name='entrar_instituicao'
    ),

    path(
        'sair/',
        sair,
        name='sair'
    ),


    # =====================================================
    # CADASTRO
    # =====================================================

    path(
        'cadastro-aluno/',
        cadastro_aluno,
        name='cadastro_aluno'
    ),


    # =====================================================
    # VAGAS PÚBLICAS
    # =====================================================

    path(
        'vagas/',
        lista_vagas,
        name='lista_vagas'
    ),

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


    # =====================================================
    # CANDIDATURAS DO ALUNO
    # =====================================================

    path(
        'minhas-candidaturas/',
        minhas_candidaturas,
        name='minhas_candidaturas'
    ),


    # =====================================================
    # ÁREA DO ALUNO
    # =====================================================

    path(
        'area-aluno/',
        area_aluno,
        name='area_aluno'
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
        'curriculo-aluno/',
        curriculo_aluno,
        name='curriculo_aluno'
    ),


    # =====================================================
    # ÁREA DA EMPRESA
    # =====================================================

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
        'perfil-empresa/',
        perfil_empresa,
        name='perfil_empresa'
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
        'empresa/trocar-senha/',
        trocar_senha_empresa,
        name='trocar_senha_empresa'
    ),


    # =====================================================
    # ÁREA DA INSTITUIÇÃO
    # =====================================================

    path(
        'area-instituicao/',
        area_instituicao,
        name='area_instituicao'
    ),


    # =====================================================
    # GERENCIAR ALUNOS
    # =====================================================

    path(
        'area-instituicao/alunos/',
        gerenciar_alunos,
        name='gerenciar_alunos'
    ),


    # =====================================================
    # GERENCIAR EMPRESAS
    # =====================================================

    path(
        'area-instituicao/empresas/',
        gerenciar_empresas,
        name='gerenciar_empresas'
    ),


    # =====================================================
    # GERENCIAR VAGAS
    # =====================================================

    path(
        'area-instituicao/vagas/',
        gerenciar_vagas,
        name='gerenciar_vagas'
    ),


    # -----------------------------------------------------
    # APROVAR VAGA
    # -----------------------------------------------------

    path(
        'area-instituicao/vagas/<int:vaga_id>/aprovar/',
        aprovar_vaga,
        name='aprovar_vaga'
    ),


    # -----------------------------------------------------
    # REJEITAR VAGA
    # -----------------------------------------------------

    path(
        'area-instituicao/vagas/<int:vaga_id>/rejeitar/',
        rejeitar_vaga,
        name='rejeitar_vaga'
    ),


    # -----------------------------------------------------
    # ENCERRAR VAGA
    # -----------------------------------------------------

    path(
        'area-instituicao/vagas/<int:vaga_id>/encerrar/',
        encerrar_vaga_instituicao,
        name='encerrar_vaga_instituicao'
    ),


    # -----------------------------------------------------
    # REABRIR VAGA
    # -----------------------------------------------------

    path(
        'area-instituicao/vagas/<int:vaga_id>/reabrir/',
        reabrir_vaga,
        name='reabrir_vaga'
    ),


    # =====================================================
    # GERENCIAR CANDIDATURAS
    # =====================================================

    path(
        'area-instituicao/candidaturas/',
        gerenciar_candidaturas,
        name='gerenciar_candidaturas'
    ),


    # =====================================================
    # RECUPERAÇÃO DE SENHA
    # =====================================================

    path(
        'esqueci-senha/',
        auth_views.PasswordResetView.as_view(
            template_name='vagas/autenticacao/password_reset.html'
        ),
        name='password_reset'
    ),

    path(
        'esqueci-senha/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='vagas/autenticacao/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'redefinir-senha/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='vagas/autenticacao/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'redefinir-senha/concluido/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='vagas/autenticacao/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]


# =========================================================
# ARQUIVOS DE MÍDIA
# =========================================================

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)