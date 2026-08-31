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
    sair
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
]
