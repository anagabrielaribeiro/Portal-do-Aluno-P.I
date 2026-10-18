# views de consentimento: mostrar a lista e revogar um consentimento

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import Consentimento, SolicitacaoExclusao
from .mapeamento import finalidades_de_consentimento, dados_obrigatorios
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail



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
def meus_consentimentos(request):
    # pega só os consentimentos do aluno logado
    consentimentos = request.user.aluno.consentimentos.all()

    # se o aluno ainda não tem consentimento, aparece popup
    mostrar_popup = not consentimentos.exists()

    return render(request, 'privacidade_lgpd/meus_consentimentos.html', {
        'consentimentos': consentimentos,
        'mostrar_popup' : mostrar_popup,
        'finalidades': finalidades_de_consentimento(),
        'obrigatorios' : dados_obrigatorios(),
    })



# cria um consentimento pra cada finalidade quando o aluno clica "li e concordo"
@never_cache
@login_required
@somente_aluno
@require_POST
def aceitar_termos(request):
    aluno = request.user.aluno  # pega o aluno ligado ao usuário logado

    # as caixas marcadas são as finalidades que o aluno aceitou
    aceitas = request.POST.getlist('finalidades')

    # percorre cada finalidade e cria um Consentimento pra cada uma
    for finalidade in finalidades_de_consentimento():
        # se já decidiu antes sobre essa finalidade, não cria de novo
        if aluno.consentimentos.filter(finalidade=finalidade).exists():
            continue
        Consentimento.objects.create(aluno=aluno, finalidade=finalidade, aceito=(finalidade in aceitas))

    request.session['termos_aceitos'] = True
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


# exportar o Lgpd e pede senha para baixar
@never_cache
@login_required
@somente_aluno
@require_POST
def exportar_dados_json(request):
    aluno = request.user.aluno
    
    if not request.user.check_password(request.POST.get('senha', '')):
        messages.error(request, 'Senha incorreta')
        return redirect('meus_consentimentos')

    # Dados da vida acadêmica (Matrículas)
    lista_matriculas = [{
        'codigo': m.codigo,  
        'curso': m.curso.nome,
        'status': m.get_status_display(),
        'periodo_letivo': m.periodo_letivo,
        'data_matricula': m.data_matricula,
    } for m in aluno.matriculas.select_related('curso')]

    # Consentimentos LGPD
    lista_consentimentos = [{
        'finalidade': c.finalidade,
        'aceito': c.aceito,
        'versao_termo': c.versao_termo,
        'data_registro': c.data_registro,
        'data_revogacao': c.data_revogacao,
    } for c in aluno.consentimentos.all()]
    
    # Solicitações de Exclusão
    lista_pedidos = [{'data_pedido': p.data_pedido, 'status': p.get_status_display()} for p in aluno.solicitacoes_exclusao.all()]
    
    # Boletos (Financeiro)
    lista_boletos = [{'referencia': b.mes_referencia, 'valor': float(b.valor), 'pago': b.pago, 'vencimento': b.vencimento} for b in aluno.boletos.all()]
    
    # Tarefas (Agenda)
    lista_tarefas = [{'titulo': t.titulo, 'concluida': t.concluida, 'data': t.data_criacao} for t in aluno.tarefas.all()]
    
    # Documentos e Certificados
    lista_docs = [{'tipo': d.get_tipo_display(), 'status': d.get_status_display(), 'data': d.data_solicitacao} for d in aluno.documentos_solicitados.all()]
    lista_certs = [{'titulo': c.titulo, 'data': c.data} for c in aluno.certificados.all()]
            
    dados = {
        'identificacao':{
            'ra': aluno.ra,
            'nome': aluno.nome,
            'nome_social': aluno.nome_social,
            'nome_exibicao': aluno.nome_exibicao,
            'cpf': aluno.cpf,
            'rg': aluno.rg,
            'data_nascimento': str(aluno.data_nascimento),
            'sexo': aluno.get_sexo_display(),
        },
        'contato':{
            'email': request.user.email,
            'telefone': aluno.telefone,
            'endereco': aluno.endereco,
        },
        'acesso': {'ultimo_ip_acesso': request.user.ultimo_ip_acesso},
        'vida_academica': lista_matriculas,
        'financeiro': lista_boletos,
        'tarefas_pessoais': lista_tarefas,
        'documentos_institucionais': lista_docs,
        'certificados_enviados': lista_certs,
        'consentimentos': lista_consentimentos,
        'solicitacoes_de_exclusao': lista_pedidos,
    }

    response = JsonResponse(dados, json_dumps_params={'ensure_ascii': False, 'indent': 4})
    response['Content-Disposition'] = 'attachment; filename="meus_dados_portal_pi.json"'
    
    return response



@never_cache
@login_required
@somente_aluno
@require_POST
def solicitar_exclusao(request):
    aluno = request.user.aluno

    # se já existe um pedido em andamento, não cria outro 
    if aluno.solicitacoes_exclusao.filter(status='pendente').exists():
        messages.info(request, 'Você já tem uma solicitação de exclusão em andamento.')
        return redirect('meus_consentimentos')
    pedido = SolicitacaoExclusao.objects.create(aluno=aluno)  # o pedido fica salvo no banco

    try:
        send_mail(
            subject='Pedido de exclusão de dados recebido',
            message = f'Recebemos seu pedido (protocolo {pedido.id}). A secretaria acadêmica entrará em contato em até 48 horas',
            from_email = None,
            recipient_list = [request.user.email],
        )
        menssages.sucess(request, f'Pedido registrado (protocolo {pedido.id}). Enviamos uma confirmação para o email')
    except Exception:
        # o pedido já está salvo então o erro não da problema na pagina
        messages.warning(request, f"Pedido registrado (protocolo {pedido.id}), mas não conseguimos enviar o e-mail de confirmação.")

    request.session['termos_aceitos'] = True # o context processor não precisa mais consultar 
    return redirect('meus_consentimentos')
    return response
