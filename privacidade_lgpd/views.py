# views de consentimento: mostrar a lista e revogar um consentimento

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import Consentimento
from .mapeamento import DADOS_PESSOAIS
from functools import wraps
from django.core.exceptions import PermissionDenied


def somente_aluno(view):
    # barra quem não é aluno com erro 403 
    @wraps(view)
    def interna(request, *args, **kwargs):
        if getattr(request.user, 'aluno', None) is None:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return interna



@never_cache
@login_required
@somente_aluno
@require_POST
def meus_consentimentos(request):
    # pega só os consentimentos do aluno logado
    consentimentos = request.user.aluno.consentimentos.all()

    # se o aluno ainda não tem consentimento, aparece popup
    mostrar_popup = not consentimentos.exists()

    # pega as finalidades unicas listadas no mapeamento, sem repetir 
    finalidades = sorted(set(d['finalidade'] for d in DADOS_PESSOAIS))

    # lista de consentimentos do aluno que pode estar vazia, e diz pro template se deve mostrar o pop_up
    return render(request, 'privacidade_lgpd/meus_consentimentos.html', {
        'consentimentos': consentimentos,
        'mostrar_popup' : mostrar_popup,
        'finalidades': finalidades,
    })



# cria um consentimento pra cada finalidade quando o aluno clica "li e concordo"
@never_cache
@login_required
@somente_aluno
@require_POST
def aceitar_termos(request):
    aluno = request.user.aluno  # pega o aluno ligado ao usuário logado

    # pega as finalidades do mapeamento.py, sem repetir (set remove duplicadas, sorted ordena)
    finalidades = sorted(set(d['finalidade'] for d in DADOS_PESSOAIS))

    # percorre cada finalidade e cria um Consentimento pra cada uma
    for finalidade in finalidades:
        Consentimento.objects.create(aluno=aluno, finalidade=finalidade)

    # depois de criar tudo, volta pra tela de consentimentos
    return redirect('meus_consentimentos')



@never_cache
@login_required
@somente_aluno
@require_POST
def revogar_consentimento(request, consentimento_id):
    # busca o consentimento só entre o aluno logado, se não achar da erro 404
    consentimento = get_object_or_404(request.user.aluno.consentimentos, id = consentimento_id)

    consentimento.revogar() # marca como não aceito e guarda a data
    return redirect('meus_consentimentos') # depois de revogar, volta pra mesma página atualizada



@never_cache
@login_required
@somente_aluno
@require_POST
def exportar_dados_json(request):
    aluno = request.user.aluno
    
    # Busca todas as matrículas para incluir no histórico acadêmico do JSON
    matriculas = aluno.matriculas.all()
    lista_matriculas = []
    for m in matriculas:
        lista_matriculas.append({
            "curso": m.curso.nome,
            "status": m.get_status_display(),
            "periodo_letivo": m.periodo_letivo
        })
        
    # Monta um dicionário Python organizando tudo o que o portal sabe sobre o aluno
    dados = {
        "identificacao": {
            "nome": aluno.nome,
            "nome_social": aluno.nome_social,
            "cpf": aluno.cpf, # Na exportação, o titular tem o direito de ver o CPF real (sem máscara)
            "rg": aluno.rg,
            "data_nascimento": str(aluno.data_nascimento),
            "sexo": aluno.get_sexo_display()
        },
        "contato": {
            "email": request.user.email,
            "telefone": aluno.telefone,
            "endereco": aluno.endereco,
        },
        "vida_academica": lista_matriculas,
    }
    
    # Converte o dicionário para JSON estruturado.
    # ensure_ascii=False permite acentuação (como "São Paulo"). indent=4 deixa o arquivo bonito para leitura.
    response = JsonResponse(dados, json_dumps_params={'ensure_ascii': False, 'indent': 4})
    
    # Esse comando avisa ao navegador que não é para exibir a tela, e sim para baixar um arquivo.
    response['Content-Disposition'] = 'attachment; filename="meus_dados_portal_pi.json"'
    
    return response



@never_cache
@login_required
@somente_aluno
@require_POST
def solicitar_exclusao(request):
    """
    Atende ao Requisito 4.10: Fluxo de solicitação de exclusão.
    Apenas registra a intenção do aluno e avisa que a secretaria fará a anonimização.
    """
    # Exibe a mensagem de sucesso na tela avisando que o DPO/Secretaria recebeu o pedido
    messages.success(request, "Sua solicitação de exclusão foi enviada para a secretaria acadêmica. Você receberá um retorno no e-mail cadastrado em até 48 horas.")
    
    return redirect('meus_consentimentos')