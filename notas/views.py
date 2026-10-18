from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from matriculas.models import Matricula
from notas.models import Nota
from calendario_horarios.models import Frequencia

@never_cache
@login_required
def notas_faltas(request):
    try:
        aluno = request.user.aluno
    except AttributeError:
        return redirect('/gestao-portal/')

    # Busca a matrícula ativa para exibir dados apenas do semestre atual
    matricula_atual = Matricula.objects.filter(aluno=aluno, status='ativa').first()

    notas = []
    frequencias = []

    if matricula_atual:
        # Busca as notas da matrícula ativa e ordena pela data
        notas = Nota.objects.filter(matricula=matricula_atual).order_by('-data')
        # Busca as faltas
        frequencias = Frequencia.objects.filter(matricula=matricula_atual).order_by('-data')

    context = {
        'matricula_atual': matricula_atual,
        'notas': notas,
        'frequencias': frequencias
    }
    
    return render(request, 'notas/notas_faltas.html', context)