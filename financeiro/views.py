from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Boleto
from django.views.decorators.cache import never_cache

@never_cache
@login_required # garante que só usuário autenticado acessa
def financeiro(request): # mostra o demonstrativo financeiro
    aluno = request.user.aluno # request.user é o Usuario logado
    boletos = Boleto.objects.filter(aluno=aluno)  # traz só os boletos desse aluno, ofiltro que impede um aluno ver o boleto de outro
   

    return render(request, 'financeiro/financeiro.html', {'boletos': boletos})
    # manda a lista pro template
