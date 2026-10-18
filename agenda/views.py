from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from tarefas.models import Tarefa

@login_required
def minha_agenda(request):
    if not hasattr(request.user, 'aluno'):
        return redirect('/gestao-portal/')
        
    # Puxa apenas as tarefas que ainda não foram concluídas pelo aluno
    tarefas_pendentes = Tarefa.objects.filter(aluno=request.user.aluno, concluida=False).order_by('-data_criacao')
    
    return render(request, 'agenda/agenda.html', {'tarefas': tarefas_pendentes})