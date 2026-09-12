from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Aluno
from .forms import AlunoContatoForm

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

    # Busca todo o histórico acadêmico do aluno
    todas_matriculas = aluno.matriculas.all().order_by('-periodo_letivo')

    historico_notas = []
    historico_financeiro = []

    # trata o envio do formulario de telefone e endereco, a página ve pra ca quando o aluo clica em salvar
    if request.method == 'POST': 
        form = AlunoContatoForm(request.POST, instance=aluno) # request.Post tem os dados digitados e o instance=aluno não deixa criar um aluno novo e sim atualizar
        if form.is_valid(): # is_valid() roda as validaões do form/model como campo origatório
            form.save() # salva no bd
            messages.success(request, 'Dados de contato atualizados com sucesso.')
            return redirect('dados_pessoais')# redireciona de volta pra mesma pagina 
    else:
        form = AlunoContatoForm(instance=aluno)

    # dados que serão enviado para o html
    context = {
        'aluno': aluno,
        'matricula_atual': matricula_atual,
        'todas_matriculas': todas_matriculas,
        'historico_notas': historico_notas,
        'historico_financeiro': historico_financeiro,
        'form': form,
    }
    # renderiza a pagina 
    return render(request, 'alunos/dados_pessoais.html', context)