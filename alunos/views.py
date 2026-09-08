from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Aluno

# se não estiver logado redireciona para a tela Login
@login_required

# cria uma função para mostraros dados pessoais do aluno
def dados_pessoais(request):

    # tenta buscar o objeto Aluno relacionado ao usuário que está logado 
    try:
        aluno = request.user.aluno 
    except Aluno.DoesNotExist: # caso o usuário esteja logado mas nã tenha cadastro mostra a mensagem
        messages.error(request, 'Não encontramos um cadastro de aluno vinculado a essa conta.')
        return redirect('dashboard') # ajustar



    # busca a matricula ativa do aluno
    matricula_atual = aluno.matriculas.filter(status='ativa').select_related('curso', 'turma').first()
   

    # dados que serão enviado para o html
    context = {
        'aluno': aluno,
        'matricula_atual': matricula_atual,
    }
    # renderiza a pagina 
    return render(request, 'alunos/dados_pessoais.html', context)