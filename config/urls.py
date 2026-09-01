from django.contrib import admin
from django.urls import path
from vagas.views import inicio, lista_vagas, detalhe_vaga, entrar, candidatar
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
    criar_vaga
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='inicio'),
    path('entrar/', entrar, name='entrar'),
    path('vagas/', lista_vagas, name='lista_vagas'),
    path('vagas/<int:vaga_id>/', detalhe_vaga, name='detalhe_vaga'),
    path('vagas/<int:vaga_id>/candidatar/', candidatar, name='candidatar'),
    path('minhas-candidaturas/', minhas_candidaturas, name='minhas_candidaturas'),
    path('sair/', sair, name='sair'),
    path('area-aluno/', area_aluno, name='area_aluno'),
    path('area-empresa/', area_empresa, name='area_empresa'),
    path('criar-vaga/', criar_vaga, name='criar_vaga'),

]
