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
@require_POST
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

    # percorre cada finalidade e cria um Consentimento pra cada uma
    for finalidade in finalidades_de_consentimento():
        # só cria se o aluno não tem consentimento ativo pra essa finalidade
        if not aluno.consentimentos.filter(finalidade=finalidade, aceito=True).exists():
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


# exportar o Lgpd e pede senha para baixar
@never_cache
@login_required
@somente_aluno
@require_POST
def exportar_dados_json(request):
    aluno = request.user.aluno
    
    # pede a senha de nov, para baixar por conta dos dados pessoais no arquivo
    if not request.usar.check_password(request.POST.get('senha', '')):
        messages.error(request, 'Senha incorreta')
        return redirect('meus_consentimentos')

    lista_matriculas = []
    for m in aluno.matriculas.select_related('curso'):
        lista_matriculas.append({
            'codigo': m.codigo,  
            'curso': m.curso.nome,
            'status': m.get_status_display(),
            'periodo_letivo': m.periodo_letivo,
            'data_matricula': m.data_matricula,
        })

        lista_consentimentos = []
        for c in aluno.consentimento.all():
            lista_consentimentos.append({
                'finalidade': c.finalidade,
                'aceito': c.aceito,
                'versao_termo': c.versao_termo,
                'data_registro': c.data_registro,
                'data_revogacao': c.data_revogacao,
            })
        
        lista_pedidos = []
        for p in aluno.solicitacoes_exclusao.all():
            lista_pedidos.append({'data_pedido': p.data_pedido, 'status': p.get_status_display()})

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
            'consentimentos': lista_consentimentos,
            'solicitacoes_de_exclusao': lista_pedidos,
            # colocar notas, boletos e calendarios seguindo o mesmo padrão
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
    aluno = request.user.aluno

    # se já existe um pedido em andamento, não cria outro 
    if aluno.solicitacoes_exclusao.filter(status='pendente').exists():
        messages.info(request, 'Você já tem uma solicitação de exclusão em andamento.')
        return redirect('meus_consentimentos')
    pedido = SolicitacaoExclusao.objects.create(aluno=aluno)  # o pedido fica salvo no banco

    try:
        send_mail(
            subject='Pedido de exclusão de dados recebido',
            message = f'Recebemos seu pedido (protocolo{pedido.id}). A secretaria acadêmica entrará em contato em até 48 horas',
            from_email = None,
            recipient_list = [request.user.email],
        )
        menssages.sucess(request, f'Pedido registrado (protocolo {pedido.id}). Enviamos uma confirmação para o email')
    except Exception:
        # o pedido já está salvo então o erro não da problema na pagina
        messages.warning(request, f"Pedido registrado (protocolo {pedido.id}), mas não conseguimos enviar o e-mail de confirmação.")

    return redirect('meus_consentimentos')
