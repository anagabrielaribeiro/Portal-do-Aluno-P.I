from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from matriculas.models import Matricula
from .models import Frequencia, Turma

@login_required
def meu_calendario(request):
    try:
        aluno = request.user.aluno
    except AttributeError:
        # Se for colaborador ou não tiver perfil de aluno, manda para o painel admin
        return redirect('/gestao-portal/')

    # Busca apenas a matrícula ativa do aluno atual
    matricula_atual = Matricula.objects.filter(aluno=aluno, status='ativa').first()

    grade_horaria = []
    frequencias = []

    if matricula_atual:
        # Como o modelo original permitia que a matrícula tivesse apenas 1 turma, 
        # puxamos essa turma (se a modelagem tivesse N turmas, faríamos um .filter())
        turma = matricula_atual.turma
        
        # Aqui, na prática, buscaríamos os horários (dia/hora/sala). 
        # Como o model 'academico_horario_aula' ainda não foi mapeado no models.py original do ingest,
        # vamos preparar a view para enviar os dados básicos da disciplina e professor da turma ativa.
        grade_horaria = [{
            'disciplina': turma.Disciplina.nome,
            'codigo': turma.Disciplina.codigo,
            'professor': turma.Professor.nome,
            'sala': f"Sala {turma.Sala.numero} - Bloco {turma.Sala.bloco}",
            'periodo': turma.periodo
        }]

        # Puxa o resumo de faltas e presenças dessa matrícula
        frequencias = Frequencia.objects.filter(matricula=matricula_atual)

    context = {
        'matricula_atual': matricula_atual,
        'grade_horaria': grade_horaria,
        'frequencias': frequencias
    }
    
    return render(request, 'calendario_horarios/calendario.html', context)