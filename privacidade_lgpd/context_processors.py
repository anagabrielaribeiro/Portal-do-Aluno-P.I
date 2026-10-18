from .models import Consentimento
from .mapeamento import finalidades_de_consentimento
# faz o pop-up aparecer até o aluno aceitar os termos, em qualquer página

def termos_pendentes(request):
    sem_popup = {'mostrar_popup': False, 'finalidades': []}

    if not request.user.is_authenticated:
        return sem_popup

    # se a sessão ká sabe que o aluno aceitou, não consulta o banco
    if request.session.get('termos_aceitos'):
        return sem_popup

    # colaborador não ve popup
    aluno = getattr(request.user, 'aluno', None)
    if aluno is None:
        return sem_popup
    
    if aluno.consentimentos.exists():
        request.session['termos_aceitos'] = True # guarda para não consultar de novo
        return sem_popup

    return {'mostrar_popup': True, 'finalidades': finalidades_de_consentimento()}


def lgpd_context(request):
    if not request.user.is_authenticated or getattr(request.user, 'aluno', None) is None:
        return {'mostrar_popup': False}

    # Lógica para alunos
    tem_consentimentos = request.user.aluno.consentimentos.exists()
    return {'mostrar_popup': not tem_consentimentos}