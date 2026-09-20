from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Boleto
@login_required # garante que só usuário autenticado acessa

# mostra o demonstrativo financeiro
def financeiro(request):
    aluno = request.user.aluno # request.user é o Usuario logado
    boletos = Boleto.objects.filter(aluno=aluno)  # traz só os boletos desse aluno, ofiltro que impede um aluno ver o boleto de outro
   

    return render(request, 'financeiro/financeiro.html', {'boletos': boletos})
    # manda a lista pro template
