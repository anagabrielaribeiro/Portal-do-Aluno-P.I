# views de consentimento: mostrar a lista e revogar um consentimento

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Consentimento


@login_required
def meus_consentimentos(request):
    # pega só os consentimentos do aluno logado
    consentimentos = request.user.aluno.consentimentos.all()
    return render(request, 'privacidade_lgpd/meus_consentimentos.html', {
        'consentimentos': consentimentos,
    })


@login_required
@require_POST
def revogar_consentimento(request, consentimento_id):
    # pega o consentimento pelo id, mas só se for do aluno logado 
    consentimento = request.user.aluno.consentimentos.get(id=consentimento_id)

    consentimento.revogar()# chama o método que já criamos no model, que marca a data de revogação
    return redirect('meus_consentimentos') # depois de revogar, volta pra mesma página atualizada