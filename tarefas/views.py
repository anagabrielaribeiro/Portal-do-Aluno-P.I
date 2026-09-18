from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tarefa

@login_required
def lista_tarefas(request):
    aluno = request.user.aluno
    # pega o aluno ligado ao usuario que esta logado

    tarefas = Tarefa.objects.filter(aluno=aluno).order_by('-data_criacao') # o sinal de menos na frente inverte a ordem, mostrando a mais recente primeiro
    # busca só as tarefas desse aluno
   
    return render(request, 'tarefas/lista.html', {'tarefas': tarefas})
    # manda a lista de tarefas pro template mostrar


@login_required
def criar_tarefa(request):
    if request.method == 'POST': # se o aluno enviou o formulario preenchido (POST)
        
        Tarefa.objects.create(
            aluno=request.user.aluno,
            titulo=request.POST.get('titulo'),
            descricao=request.POST.get('descricao'),
        )
        # cria a tarefa nova, sempre ao aluno logado

        return redirect('lista_tarefas')
        # depois de salvar, volta pra lista, evita reenvio do formulario se der F5

    return render(request, 'tarefas/form.html')
    # se nao for POST, so mostra o formulario vazio pra preencher


@login_required
def editar_tarefa(request, pk):
    tarefa = request.user.aluno.tarefas.get(pk=pk)
    # busca a tarefa pelo id, mas só dentro das tarefas do aluno logado
    # se o id não existir ou for de outro aluno, erro

    if request.method == 'POST':
        tarefa.titulo = request.POST.get('titulo')
        tarefa.descricao = request.POST.get('descricao')
        tarefa.concluida = 'concluida' in request.POST
        # checkbox so vem no POST quando esta marcado

        tarefa.save()
        # grava as alteracoes no banco

        return redirect('lista_tarefas')

    return render(request, 'tarefas/form.html', {'tarefa': tarefa})
    # mostra o formulario ja preenchido com os dados atuais da tarefa


@login_required
def apagar_tarefa(request, pk):
    tarefa = request.user.aluno.tarefas.get(pk=pk)
    #  so apaga se for do proprio aluno

    tarefa.delete()
    # remove a tarefa do banco

    return redirect('lista_tarefas')