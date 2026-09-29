from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def area_instituicao(request):
    return render(
        request,
        'vagas/instituicao/area_instituicao.html'
    )