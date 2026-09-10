from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Matricula


@login_required
def minhas_matriculas(request):
    aluno = request.user.aluno

    # busca todas as matrículas do aluno, já trazendo curso e turma junto
    # select_related evita fazer uma query separada pra cada relação
    matriculas = (
        Matricula.objects
        .filter(aluno=aluno)
        .select_related('curso', 'turma')
        .order_by('-data_matricula')
    )

    # a matrícula em destaque no topo da tela é a que está ativa
    matricula_atual = matriculas.filter(status='ativa').first()

    # o histórico mostra todas as outras, exceto a que já apareceu em destaque
    if matricula_atual:
        historico = matriculas.exclude(pk=matricula_atual.pk)
    else:
        historico = matriculas

    # ordena as matriculas de mais antiga para a mais recente 
    primeira_matricula = matriculas.order_by('data_matricula').first()
    # Pega a data da primeira matrícula
    inicio_vinculo = primeira_matricula.data_matricula if primeira_matricula else None


    # dados que serão enviados para o HTM
    context = {
        'matricula_atual': matricula_atual,
        'historico': historico,
        'inicio_vinculo': inicio_vinculo,
    }
    # renderiza a pagina 
    return render(request, 'matriculas/minhas_matriculas.html', context)