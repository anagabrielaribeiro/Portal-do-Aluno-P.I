from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

import pyotp
import qrcode
import io
import base64

from .models import Usuario


# Quantidade máxima de tentativas de login antes do bloqueio.
limite_tentativas = 5

# Tempo de bloqueio da conta, em minutos.
tempo_bloqueio = 15


def obter_ip(request):
    """
    Obtém o endereço IP do usuário que está acessando o sistema.

    HTTP_X_FORWARDED_FOR é utilizado quando o sistema está atrás
    de um servidor ou serviço de hospedagem.
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

def login_view(request):

    # Verifica se o formulário de login foi enviado.
    if request.method == 'POST':

        username = request.POST.get('username')
        senha = request.POST.get('password')

        # Procura o usuário pelo nome de usuário.
        try:
            usuario = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            usuario = None

        # Verifica se a conta está temporariamente bloqueada.
        if usuario and usuario.esta_bloqueado():
            messages.error(
                request,
                'Conta bloqueada temporariamente. '
                'Tente novamente mais tarde.'
            )

            return render(
                request,
                'autenticacao/login.html'
            )

        # Verifica usuário e senha.
        usuario_autenticado = authenticate(
            request,
            username=username,
            password=senha
        )

        # -------------------------------------------------
        # SENHA CORRETA
        # -------------------------------------------------

        if usuario_autenticado is not None:

            # Zera o contador de tentativas erradas.
            usuario_autenticado.tentativas_login_falha = 0

            usuario_autenticado.save(
                update_fields=['tentativas_login_falha']
            )

            # Guarda temporariamente o usuário na sessão.
            #
            # O login definitivo só acontecerá depois
            # que o segundo fator for validado.
            request.session['usuario_pendente_id'] = (
                usuario_autenticado.id
            )

            # Verifica se o usuário já configurou o 2FA.
            if usuario_autenticado.autentificacao_dois_fatores:

                return redirect('verificar_2fa')

            # Primeiro acesso: precisa configurar o 2FA.
            return redirect('ativar_2fa')

        # -------------------------------------------------
        # SENHA INCORRETA
        # -------------------------------------------------

        if usuario:

            usuario.tentativas_login_falha += 1

            # Se atingiu o limite, bloqueia a conta.
            if usuario.tentativas_login_falha >= limite_tentativas:
                usuario.bloqueio_ate = (
                    timezone.now()
                    + timedelta(minutes=tempo_bloqueio)
                )

            usuario.save(
                update_fields=[
                    'tentativas_login_falha',
                    'bloqueio_ate'
                ]
            )

        messages.error(
            request,
            'Usuário ou senha incorretos.'
        )

    # Exibe o formulário de login.
    return render(
        request,
        'autenticacao/login.html'
    )


# ---------------------------------------------------------
# ATIVAÇÃO DO 2FA
# ---------------------------------------------------------

def ativar_2fa_view(request):

    # Recupera o usuário que acabou de acertar a senha.
    usuario_id = request.session.get(
        'usuario_pendente_id'
    )

    # Se não existe usuário pendente, volta para o login.
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    # Cria a chave secreta apenas se ainda não existir.
    if not usuario.chave_2fa:

        usuario.chave_2fa = pyotp.random_base32()

        usuario.save(
            update_fields=['chave_2fa']
        )

    # Cria o objeto responsável pelo código TOTP.
    totp = pyotp.TOTP(usuario.chave_2fa)

    # Cria o endereço que será utilizado pelo aplicativo
    # autenticador para configurar o segundo fator.
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

            # Remove o usuário da situação pendente.
            del request.session['usuario_pendente_id']

            # Agora o login é realmente efetuado.
            login(request, usuario)

            # Registra o último login.
            usuario.ultimo_login = timezone.now()

            # Registra o IP utilizado.
            usuario.ultimo_ip_acesso = obter_ip(request)

            usuario.save(
                update_fields=[
                    'ultimo_login',
                    'ultimo_ip_acesso'
                ]
            )

            messages.success(
                request,
                'Autenticação de dois fatores ativada com sucesso.'
            )

            return redirect('dashboard')

        messages.error(
            request,
            'Código inválido. Tente novamente.'
        )

    return render(
        request,
        'autenticacao/ativar_2fa.html',
        {
            'qr_base64': qr_base64
        }
    )


# ---------------------------------------------------------
# VERIFICAÇÃO DO 2FA
# ---------------------------------------------------------

def verificar_2fa_view(request):

    # Recupera o usuário que acertou a senha.
    usuario_id = request.session.get(
        'usuario_pendente_id'
    )

    # Impede acesso direto à página.
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(
        id=usuario_id
    )

    if request.method == 'POST':

        codigo = request.POST.get('codigo')

        # Recria o TOTP utilizando a chave salva no banco.
        totp = pyotp.TOTP(
            usuario.chave_2fa
        )

        # Verifica o código informado.
        if totp.verify(codigo):

            # Remove o estado temporário da sessão.
            del request.session['usuario_pendente_id']

            # Efetua o login definitivo.
            login(request, usuario)

            # Registra data e hora do último login.
            usuario.ultimo_login = timezone.now()

            # Registra o IP do acesso.
            usuario.ultimo_ip_acesso = obter_ip(request)

            usuario.save(
                update_fields=[
                    'ultimo_login',
                    'ultimo_ip_acesso'
                ]
            )

            return redirect('dashboard')

        messages.error(
            request,
            'Código inválido. Tente novamente.'
        )

    return render(
        request,
        'autenticacao/verificar_2fa.html'
    )


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

def dashboard(request):

    # Impede que alguém acesse o dashboard sem estar logado.
    if not request.user.is_authenticated:
        return redirect('login')

    return render(
        request,
        'autenticacao/dashboard.html'
    )


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

def logout_view(request):

    # Encerra a sessão do usuário.
    logout(request)

    # Depois do logout, volta para o login.
    return redirect('login')