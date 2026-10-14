from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Usuario, LogAutenticacao
import pyotp
import qrcode
import io
import base64
from .models import Usuario, LogAuditoria
import ipaddress
import time
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import F
from django.views.decorators.http import require_POST

# Quantidade máxima de tentativas de login antes do bloqueio.
limite_tentativas = 5

# Tempo de bloqueio da conta, em minutos.
tempo_bloqueio = 15

# falhas por ip antes de bloquear o ip 
limite_tentativas_ip= 20

# minutos para digitar o código
prazo_2fa = 5 

MSG_LOGIN = 'Usuário ou senha incorretos. Se errou várias vezes, aguarde alguns minutos.'

def home_view(request):
    return render(request, 'autenticacao/home.html')  # o caminho do seu template


# usa o ultimo valor que a hospedagem adiciona 
def obter_ip(request):

    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = xff.split(',')[-1].strip() if xff else request.META.get('REMOTE_ADDR')
    # se não for um ip valido devolve none, sem erro 500 no log
    try: 
        return str(ipaddress.ip_address(ip))
    except ValueError:
        return None




# Funções Auxiliares 

def ip_bloqueado(ip):
    # contador de falhas por IP guardado no cache
    return bool(ip) and cache.get(f'falhas_ip_{ip}', 0) >= limite_tentativas_ip


# contar_falha_ip soma 1 a cada falha, ou cria o contador com validade de 15 min para a primeira vez
# ip_bloqueado só confere se o contador já passou de 20. 
# Isso serve para quem testa uma senha em várias contas
def contar_falha_ip(ip):
    if not ip:
        return
    chave = f'falhas_ip_{ip}'
    try: 
        cache.incr(chave)
    except ValueError: 
        cache.set(chave,1,tempo_bloqueio *60)


# se a conta tinha bloqueio e o prazo passou, zera o contador e limpa a data
def liberar_bloqueio_expirado(usuario):
    if usuario.bloqueio_ate and not usuario.esta_bloqueado():
        usuario.tentativas_login_falha = 0
        usuario.bloqueio_ate = None
        usuario.save(update_fields=['tentativas_login_falha', 'bloqueio_ate'])


def registrar_falha(request, usuario, acao, detalhe):
    ip = obter_ip(request)
    contar_falha_ip(ip)


    # verifica se a tentativa de login foi feita com usuario que não existe
    # se sim, cria um registro na auditoria falando que o login falhou por conta do usuario inexistente
    if usuario is None:
        LogAuditoria.objects.create(usuario=None, acao=LogAuditoria.Acao.LOGIN_FALHO,
        risco=LogAuditoria.Risco.BAIXO, ip_origem=ip,
        detalhes='Tentativas de login com usuário que não existe')
        return
    
    # atualiza no banco de dados o número de tentativas falahas do usuario
    Usuario.objects.filter(pk=usuario.pk).update(
        tentativas_login_falha=F('tentativas_login_falha') + 1
    )
    usuario.refresh_from_db() # atualiza o usuario na memória do python também


    # verifica se o usuario passou do limite máximo de erros
    if usuario.tentativas_login_falha >= limite_tentativas:
        usuario.bloqueio_ate = timezone.now() +timedelta(minutes=tempo_bloqueio) # momento do blouqueio expirar
        usuario.save(update_fields=['bloqueio_ate'])

        # se atingiu o limite, cria um registro em auditoria 
        LogAuditoria.objects.create(
            usuario= usuario,
            acao= LogAuditoria.Acao.BLOQUEIO,
            risco= LogAuditoria.Risco.CRITICO,
            ip_origem= ip,
                detalhes=f'Conta bloqueada temporariamente após {limite_tentativas} falhas'
        )
    # se não atingiu o limite, cria um registro de auditoria padrão
    else:
        LogAuditoria.objects.create(
            usuario= usuario,
            acao= acao,
            risco= LogAuditoria.Risco.MEDIO,
            ip_origem= ip,
            detalhes=f'{detalhe}: {usuario.tentativas_login_falha} de {limite_tentativas}'
        )

# lógica auxiliar de 2fa, de quando tem a senha certa, mas falta o código

# Guarda temporariamente o estado do usuário que acertou a senha, mas ainda precisa digitar o código 2FA.
def iniciar_pendente(request, usuario, tipo):
    request.session['usuario_pendente_id'] = usuario.id
    request.session['pendente_desde'] = time.time()# horario para expirar
    request.session['tipo_login'] = tipo 


# limpa os dados temporarios do 2FA da sessão
def limpar_pendente(request):
    for chave in ('usuario_pendente_id','pendente_desde', 'tipo_login'):
        request.session.pop(chave, None) # apaga a chave


# valida se ainda existe um processo de 2FA válido ativo na sessão.
def obter_pendente(request):

    # busca o id e o tempo de incio da sessão, se não tiver 
    # é porque o usuario não está na parte de 2fa e retorna
    usuario_id = request.session.get('usuario_pendente_id')
    desde = request.session.get('pendente_desde')
    if not usuario_id or not desde:
        return None


    # se o tempo de limite expirou ou o ip está bloqueado
    # limpa a sessão com o limpar_pendente e recusa o acesso
    if time.time() - desde > prazo_2fa * 60 or ip_bloqueado(obter_ip(request)):
        limpar_pendente(request)
        return None

    # se o usuario foi apagado no meio do fluxo, dá erro 500
    usuario = Usuario.objects.filter(id=usuario_id).first()
    if usuario is None or usuario.esta_bloqueado():
        limpar_pendente(request)
        return None
    return usuario


# executa quando o usuario erra o codigo 2fa 
def registrar_falha_2fa (request, usuario):
    registrar_falha(request, usuario, LogAuditoria.Acao.TOTP_FALHO, 'código TOTP inválido') 
        # se a conta foi bloqueada por tentativas, limpa os dados da sessão, avisa o usuário e encerra o fluxo.    
    if usuario.esta_bloqueado():
        limpar_pendente(request)
        messages.error(request, MSG_LOGIN)
        return True
    messages.error(request, 'Código inválido. Tente novamente')
    return False


# executa depois que o usuario acerta o codigo 2fa 
def concluir_login(request, usuario):
    tipo = request.session.get('tipo_login')
    limpar_pendente(request) # apaga as chaves teporarias 
    login(request, usuario) # função do Django

    # busca se exite perfil vinculado, e cria um um registro na auditoria de quem entrou
    aluno = getattr(usuario, 'aluno', None)
    LogAutenticacao.objects.create(
        usuario=usuario,
        ra_registrado=getattr(aluno, 'ra', ''),
        ip= obter_ip(request)
    )


    # zera as falhas só aqui, depois do 2fa conluído 
    Usuario.objects.filter(pk=usuario.pk).update(
        tentativas_login_falha=0,
        bloqueio_ate=None,
        ultimo_login=timezone.now(),
        ultimo_ip_acesso=obter_ip(request),
    )
 
    # se for colaborador, redirecionado para a gestão
    if tipo == 'colaborador':
        return redirect('/gestao-portal/')
    return redirect('dashboard')



# LOGIN
def login_view(request):
    # Verifica se o formulário de login foi enviado.
    if request.method == 'POST':
        email = request.POST.get('username')
        senha = request.POST.get('password')

        # não autentifica ip com muitas falhas
        if ip_bloqueado(obter_ip(request)):
            messages.error(request, MSG_LOGIN)
            return render(request, 'autenticacao/login.html')


        usuario = Usuario.objects.filter(email=email).first()
        if usuario: 
            liberar_bloqueio_expirado(usuario)


        # Verifica se a conta está temporariamente bloqueada.
        if usuario and usuario.esta_bloqueado():
            messages.error(request, MSG_LOGIN)
            return render(
                request,
                'autenticacao/login.html'
            )
        
        # Verifica usuário e senha.
        usuario_autenticado = authenticate(
            request,
            username=email,
            password=senha
        )


        # SENHA CORRETA
        if (usuario is not None
            and usuario_autenticado is not None
            and usuario_autenticado.pk == usuario.pk
            and hasattr(usuario_autenticado, 'aluno')):
            # guarda o usuario pendente, o contador só zera depois do 2fa
            iniciar_pendente(request, usuario_autenticado, 'aluno')

            # Verifica se o usuário já configurou o 2FA.
            if usuario_autenticado.autentificacao_dois_fatores:
                return redirect('verificar_2fa')
            # Primeiro acesso: precisa configurar o 2FA.
            return redirect('ativar_2fa')


    # SENHA INCORRETA

    # 
        registrar_falha(request, usuario, LogAuditoria.Acao.LOGIN_FALHO, 'tentativa Falha')
        messages.error(request, MSG_LOGIN)

    # Exibe o formulário de login.
    return render(
        request,
        'autenticacao/login.html'
    )


# LOGIN COLABORADOR
def login_colaborador_view(request):

    if request.method == 'POST':
        email = request.POST.get('username')
        senha = request.POST.get('password')

        if ip_bloqueado(obter_ip(request)):
            messages.error(request, MSG_LOGIN)
            return render(request, 'autenticacao/login_colaborador.html')

        usuario = Usuario.objects.filter(email=email).first()
        if usuario:
            liberar_bloqueio_expirado(usuario)


        # verifica se a conta está temporariamente bloqueada
        if usuario and usuario.esta_bloqueado():
            messages.error(request, MSG_LOGIN)
            return render(request, 'autenticacao/login_colaborador.html')

        # verifica usuario e senha
        usuario_autenticado = authenticate(
            request,
            username=email,
            password=senha
        )


        # so passa se autenticou e tem perfil de colaborador vinculado
        # impede que um aluno de entrar por aqui, mesmo com senha certa
        if (usuario is not None
            and usuario_autenticado is not None
            and usuario_autenticado.pk == usuario.pk
            and hasattr(usuario_autenticado, 'colaborador')):

            iniciar_pendente(request, usuario_autenticado, 'colaborador')

            # verrifica se o usuario já configurou o 2fa
            if usuario_autenticado.autentificacao_dois_fatores:
                return redirect('verificar_2fa')

            return redirect('ativar_2fa')

        registrar_falha(request, usuario, LogAuditoria.Acao.LOGIN_FALHO, 'Tentativa falha')
        messages.error(request, MSG_LOGIN)

        return render(
            request,
            'autenticacao/login_colaborador.html'
        )

    return render(
        request,
        'autenticacao/login_colaborador.html'
    )


# ATIVAÇÃO DO 2FA
def ativar_2fa_view(request):

    usuario = obter_pendente(request)
    if not usuario:
        return redirect('login')

    # se tiver 2fa ativo, não ve mais o QR code
    if usuario.autentificacao_dois_fatores:
        return redirect('verificar_2fa')

    # Cria a chave secreta apenas se ainda não existir.
    if not usuario.chave_2fa:
        usuario.chave_2fa = pyotp.random_base32()
        usuario.save(
            update_fields=['chave_2fa']
        )
    # Cria o objeto responsável pelo código TOTP.
    totp = pyotp.TOTP(usuario.chave_2fa)
    # Cria o endereço que será utilizado pelo aplicativo para configurar o segundo fator.
    uri_provisionamento = totp.provisioning_uri(
        name=usuario.email or usuario.username,
        issuer_name='Portal do Aluno'
    )
    # Gera o QR Code.
    qr = qrcode.make(uri_provisionamento)
    # Guarda a imagem temporariamente na memória.
    buffer = io.BytesIO()
    qr.save(
        buffer,
        format='PNG'
    )
    # Converte a imagem para Base64 para poder
    # colocá-la diretamente no HTML.
    qr_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode('utf-8')
    # Verifica se o usuário enviou o código.
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        # Confere se o código informado é válido.
        if totp.verify(codigo):
            usuario.autentificacao_dois_fatores = True
            usuario.save(
                update_fields=[
                    'autentificacao_dois_fatores'
                ]
            )
            
            messages.success(
                request,
                'Autenticação de dois fatores ativada com sucesso.'
            )

            return concluir_login(request, usuario)
        else:

            if registrar_falha_2fa(request, usuario):
                return redirect('login')
       
    return render(
        request,
        'autenticacao/ativar_2fa.html',
        {
            'qr_base64': qr_base64
        }
    )


# VERIFICAÇÃO DO 2FA
def verificar_2fa_view(request):
    usuario = obter_pendente(request)
    if not usuario:
        return redirect('login')

    # sem 2fa ativado, envia para a ativação
    if not usuario.autentificacao_dois_fatores:
        return redirect('ativar_2fa')


    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        # Recria o TOTP utilizando a chave salva no banco.
        totp = pyotp.TOTP(
            usuario.chave_2fa
        )
        # Verifica o código informado.
        if totp.verify(codigo):
            return concluir_login(request, usuario)
        else:
            if registrar_falha_2fa(request, usuario):
                return redirect('login')
       
    return render(
        request,
        'autenticacao/verificar_2fa.html'
    )


# DASHBOARD
@login_required(login_url='login')
def dashboard(request):
    if not hasattr(request.user, 'aluno'):
        return redirect('/gestao-portal/')

    return render(
        request,
        'autenticacao/dashboard.html'
    )


# LOGOUT
@require_POST # só sai por POST 
def logout_view(request):
    # Encerra a sessão do usuário.
    logout(request)
    # Depois do logout, volta para o login.
    return redirect('login')


