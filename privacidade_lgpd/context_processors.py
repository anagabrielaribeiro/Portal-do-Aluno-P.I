from .models import Consentimento
from .mapeamento import DADOS_PESSOAIS
# ideia é fazer o pop-up aparecer até o aluno aceitar os termos 
# mesma lógica da view, checa se o aluno logado ainda não tem nenhu consentimento registrado, e monta a lista de finalidades
# assim deixa essas duas variaveis disponiveis em qualquer template, sem repetir a lógica da view. 

def termos_pendentes(request):
    
    
    # Verifica se o usuário está logado e se é um aluno
    if request.user.is_authenticated and hasattr(request.user, 'aluno'):
        consentimentos = request.user.aluno.consentimentos.all() # Busca os consentimentos que o aluno já aceitou
        finalidades = sorted(set(d['finalidade'] for d in DADOS_PESSOAIS)) # Cria a lista de finalidades sem repetir nomes

        return {
            # Mostra o pop-up se o aluno ainda NÃO tiver nenhum consentimento salvo
            'mostrar_popup': not consentimentos.exists(),
            'finalidades': finalidades,
        }
    return {'mostrar_popup': False, 'finalidades': []}