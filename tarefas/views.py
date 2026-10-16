from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tarefa
from django.views.decorators.cache import never_cache
from functools import wraps


# wrapper função interna executa a as validações de segurança antes de 
# deixar a pagina carregar
def aluno_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        # Tenta pegar o aluno vinculado; se não existir ou der erro, bloqueia com 403
        aluno = getattr(request.user, 'aluno', None)
        if not aluno:
            raise PermissionDenied
            
        request.aluno = aluno
        return view(request, *args, **kwargs)
        
    return wrapper


# só as tarefas do aluno logado, da mais recente para a mais antiga
@never_cache 
@login_required
def lista_tarefas(request):
    aluno = request.user.aluno
    tarefas = Tarefa.objects.filter(aluno=aluno).order_by('-data_criacao') 
    return render(request, 'tarefas/lista.html', {'tarefas': tarefas})
    

@never_cache # never_cache impede que o navegador salve a pag em cache
@login_required # usa apenas usuarios autenticados 
@aluno_required # se o usuario loga é aluno 
def criar_tarefa(request):
    if request.method == 'POST': 
        form = TarefaForm(request.POST)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.aluno = request.aluno
            tarefa.save()
            return redirect('lista_tarefas')
    else:
        form = TarefaForm()
    return render(request, 'tarefa/form.html', {'form': form})



@never_cache
@login_required
@aluno_required
def editar_tarefa(request, pk):
    # 404 se o id não existir ou se a tarefa for de outro aluno
    tarefa = get_object_or_404(Tarefa, pk=pk, aluno=request.aluno)
    if request.method == 'POST':
        form = TarefaEdicaoForm(request.POST, isinstance=tarefa) # intance faz o form atualizar a tarefa existemte
        if form.is_valid():
            form.save()
            return redirect('lista_tarefas')
    else: 
        # na primeira abertura, o form já vem preenchidos com os dados atuais
        form = TarefaEdicaoForm(isinstance=tarefa)
    return render(request, 'tarefas/form.html', {'form': form,'tarefa': tarefa})




@never_cache
@login_required
@aluno_required
@require_POST # restringe a view para aceitar apenas POST (sem get)
def apagar_tarefa(request, pk):
    # só encontra a tarefa do proprio aluno, o pk é o id da tarefa não do usuario
    tarefa = get_object_or_404(Tarefa, pk=pk, aluno=request.aluno)
    tarefa.delete()
    return redirect('lista_tarefas')

