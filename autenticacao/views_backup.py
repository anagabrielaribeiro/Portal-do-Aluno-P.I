from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
import pyotp
import qrcode
import io
import base64 

from .models import Usuario

limite_tentativas = 5
tempo_bloqueio = 15

def obter_ip(request):
    # busca o IP de quem está acessando o site
    # HTTP_X_FORWARDED_FOR só existe quando o site está atras de uma hospedagem
    #
    x_fowarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    # Se econtrou um Ip,pega o primeiro da lista 
    if x_fowarded_for:
        ip = x_fowarded_for.split(',')[0]
    #Se não encontrou o HTTP_X_FORWARDED_FOR, pega o ip da conexão
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



# Função principal do login
def login_view(request):

    # verifica se o usuário enviou o formulario de login
    if request.method == 'POST':
        username = request.POST.get('username') #pega o nome de usuário que veio do formulario HTML
        senha = request.POST.get('password')# pega a senha que veio do formulario 



        #               Procura o usuário no banco 

        # tenta encontrar um usuário com esse username
        try: 
            usuario = Usuario.objects.get(username=username)
        #Se não encontrar o usuário, como none    
        except Usuario.DoesNotExist: 
            usuario = None 



        #               Verificação da conta bloqueada

        # se o usuário existe e estiver bloqueado
        if usuario and usuario.esta_bloqueado():
            messages.error(request, 'Conta bloqueada temporariamete. Tente novamente mais tarde.') # mostra a mensagem erro para usuário
            return render(request, 'autenticacao/login.html')


        #               Veirifica Usuário e Senha

        # Se a veriicação der errado, recebe none
        usuario_autenticado = authenticate(request, username=username, password=senha)

        #                 Senha correta 
        # se o authenticate encontrou o usuário, a senha está correta 
        if usuario_autenticado is not None:
            # zera o contador de tentativas erradas 
            usuario_autenticado.tentativas_login_falha = 0 

            # e depois salva a alteração no banco
            usuario_autenticado.save(update_fields=['tentativas_login_falha'])



            #               Aguardar para fazer o login 

            request.session['usuario_pendente_id'] = usuario_autenticado.id


            #               Verifica se o 2F já foi

            # se já ativou, manda para a pagina onde o usuario deve digitar o código 2f
            if usuario_autenticado.autentificacao_dois_fatores:
                return redirect('verificar_2fa')
            # se não configurou manda para a pagina de configuração do 2f onde mostra o qrcod
            else:
                return redirect('ativar_2fa')



        #  Continuação da verificação da conta bloqueada
        # senha incorreta

        # só entra se o usuario existir e errou a senha
        else:
            # se p usuario existir, e errou a senha aumento o contador
            if usuario:
                usuario.tentativas_login_falha +=1

                #verifica se chegou ao limite de tentativas, se chegou bloqueia por 15 min
                if usuario.tentativas_login_falha >= limite_tentativas:
                    usuario.bloqueio_ate = timezone.now() + timedelta(minutes=tempo_bloqueio)
                usuario.save(update_fields=['tentativas_login_falha', 'bloqueio_ate']) # salva no banco, quantidade de tentativas, horario até qual está bloqueado

            # mostra a mensagem de erro
            messages.error(request, 'Usuário ou senha incorretos')

    # se o usuario apenas abriu a pagina, ou se houve erro no login
    #mostra de noo o formulário
    return render(request, 'autenticacao/login.html')


def ativar_2fa_view(request):

    # pega da sessão o ID do usuário que acabou de acertar senha
    usuario_id = request.session.get('usuario_pendente_id')

    # Se não existe usuario pendente, a pessoa tentou acessar a lagina sem passar pelo login 
    if not usuario_id:
        return redirect('login') # então volta para o lgin 

    # busca no banco o usuario usando o id
    usuario = Usuario.objects.get(id=usuario_id)




    #                   Criação da chave secreta do 2F

    # se o usuario ainda não possui uma chave
    if not usuario.chave_2fa:
        usuario.chave_2fa = pyotp.random_base32() #cria uma chave aleatória
        usuario.save(update_fields=['chave_2fa'])

    #salva a chave nobanco 
    totp = pyotp.TOTP(usuario.chave_2fa)


    #             Criação do link que vai no qrcode

    # Cria uma uri que os aplicativos autentifcadores conseguem entender
    # com o usuario, sistema e chave secreta

    uri_provsionamento = totp.provisioning_uri(
        name= usuario.email or usuario.username,
        issuer_name= 'Portal do aluno'
    )


    #             Criação do qrcode

    #cria uma imagem qr code usando a uri
    qr = qrcode.make(uri_provsionamento)

    # cria um espaço temporario na memória para guardar a imagem
    buffer = io.BytesIO() #

    # salva o qr code como png dentro da memoria
    qr.save(buffer, format='PNG')


    #              Converte a imagem para base64
    #permite colocar a imagem diretamente em HTML
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    #           Verifica se o usuario enviou o codigo

    if request.method == 'POST':
        #codigo digitado pelo usuario
        codigo = request.POST.get('codigo')

        # verifica se é valido
        if totp.verify(codigo):

            usuario.autentificacao_dois_fatores = True #se estiver correto, marca 2fa como ativado
            usuario.save(update_fields=['autentificacao_dois_fatores']) # salva no banco

            # remov da situação pendente
            del request.session['usuario_pendente_id']


            #        Faz o login

            login(request, usuario)
            usuario.ultimo_login = timezone.now() #guarda a data e hora do ultimo acesso
            usuario.ultimo_ip_acesso = obter_ip(request) # guarda o ip utilizado no login
            usuario.save(update_fields=['ultimo_login', 'ultimo_ip_acesso']) # salva no banco

            # mensagem de sucesso, depois vai para a oagina do dashboard do aluno
            messages.success(request, 'Autentificação de dois fatores ativada com sucesso')
            return redirect('dashboard')
        else:
            messages.error(request, 'Código invalido. Tente novamente.')

    return render(request, 'autenticacao/ativar_2fa.html', {'qr_base64': qr_base64})


def verificar_2fa_view(request):

    # pega da sessão o ID do usuário que acabou de acertar a senha
    usuario_id = request.session.get('usuario_pendente_id')

    # Se não existe usuario pendente, a pessoa tentou acessar a pagina sem passar pelo login
    if not usuario_id:
        return redirect('login')

    # busca no banco o usuario usando o id
    usuario = Usuario.objects.get(id=usuario_id)

    #           Verifica se o usuario enviou o codigo

    if request.method == 'POST':
        #codigo digitado pelo usuario
        codigo = request.POST.get('codigo')

        # recria o totp usando a chave que já foi salva na ativação
        totp = pyotp.TOTP(usuario.chave_2fa)

        # verifica se é valido
        if totp.verify(codigo):

            # remove da situação pendente
            del request.session['usuario_pendente_id']

            #        Faz o login

            login(request, usuario)
            usuario.ultimo_login = timezone.now() #guarda a data e hora do ultimo acesso
            usuario.ultimo_ip_acesso = obter_ip(request) # guarda o ip utilizado no login
            usuario.save(update_fields=['ultimo_login', 'ultimo_ip_acesso']) # salva no banco

            return redirect('dashboard')
        else:
            messages.error(request, 'Código invalido. Tente novamente.')

    return render(request, 'autenticacao/verificar_2fa.html')


#            Função para verificar o 2Fa nos proimos logins


def verificar_2fa_view(request):

    # pega da sessão o ID do usuário que acabou de acertar a senha
    usuario_id = request.session.get('usuario_pendente_id')

    # Se não existe usuario pendente, a pessoa tentou acessar a pagina sem passar pelo login
    if not usuario_id:
        return redirect('login')

    # busca no banco o usuario usando o id
    usuario = Usuario.objects.get(id=usuario_id)

    #           Verifica se o usuario enviou o codigo

    if request.method == 'POST':
        #codigo digitado pelo usuario
        codigo = request.POST.get('codigo')

        # recria o totp usando a chave que já foi salva na ativação
        totp = pyotp.TOTP(usuario.chave_2fa)

        # verifica se é valido
        if totp.verify(codigo):

            # remove da situação pendente
            del request.session['usuario_pendente_id']

            #        Faz o login

            login(request, usuario)
            usuario.ultimo_login = timezone.now() #guarda a data e hora do ultimo acesso
            usuario.ultimo_ip_acesso = obter_ip(request) # guarda o ip utilizado no login
            usuario.save(update_fields=['ultimo_login', 'ultimo_ip_acesso']) # salva no banco

            return redirect('dashboard')
        else:
            messages.error(request, 'Código invalido. Tente novamente.')

    return render(request, 'autenticacao/verificar_2fa.html')


#      Função Logout


def logout_view(request):
    logout(request) # encerra a sessão
    return redirect('login') # depois de sair volta para o login


def login_view(request):
    return render(request, 'autenticacao/login.html')