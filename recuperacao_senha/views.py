import logging
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
import hashlib  
import smtplib
from django.core.cache import cache
from django.shortcuts import render, redirect
from autenticacao.views import obter_ip
from django.contrib.auth.forms import PasswordResetForm 
from django.core.mail import EmailMultiAlternatives  
from django.template import loader  



# Chama o logger configurado no settings.py
logger = logging.getLogger('recuperacao_senha')


LIMITE_POR_IP = 5
LIMITE_POR_EMAIL = 3
JANELA_SEGUNDOS = 3600

# mascarar o e-mail nos logs, exibindo apenas a primeira letra e o domínio
def _mascarar_email(email):
    if '@' not in email:
        return '***'
    usuario, dominio = email.split('@', 1)
    return f"{usuario[:1]}***@{dominio}"


# o Django 6.1 esconde os erros de envio do e-mail de recuperação, então a gente não ficava sabendo
# quando o SMTP falhava. Por isso o envio é feito aqui, para poder registrar se deu certo ou não
class FormularioRecuperacao(PasswordResetForm):

    # o Django chama esse método sozinho, só quando existe um usuário com o e-mail digitado
    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):

        # monta o assunto (sem quebra de linha, e-mail não aceita) e o texto do e-mail
        assunto = "".join(loader.render_to_string(subject_template_name, context).splitlines())
        corpo = loader.render_to_string(email_template_name, context)

        # cria a mensagem com remetente e destinatário
        mensagem = EmailMultiAlternatives(assunto, corpo, from_email, [to_email])

        # se existir uma versão em HTML do e-mail, anexa junto
        if html_email_template_name is not None:
            mensagem.attach_alternative(loader.render_to_string(html_email_template_name, context), "text/html")

        try:
            # entrega a mensagem para o servidor de e-mail 
            mensagem.send()
        except Exception as erro:
            # deu erro: grava a falha no log (com o e-mail mascarado) e para por aqui.
            # a tela continua igual para o usuário, para não mostrar se o e-mail existe ou não
            logger.error(f"FALHA: não foi possível enviar o e-mail de recuperação ({type(erro).__name__}, e-mail={_mascarar_email(to_email)})")
            return

        # o servidor de e-mail aceitou a mensagem, então grava o sucesso
        logger.info(f"SUCESSO: e-mail de recuperação entregue ao servidor SMTP (e-mail={_mascarar_email(to_email)})")



# controla o limite de tentativas usando o cache para evitar ataques de força bruta
def _estourou_limite(chave, limite):
    total = cache.get(chave, 0) + 1
    cache.set(chave, total, JANELA_SEGUNDOS)
    return total > limite



# Nota: não precisamos definir "success_url" em nenhuma dessas views. 
# O Django já sabe para onde redirecionar sozinho, porque ele procura automaticamente pelas urls de nome 
# 'password_reset_done' e 'password_reset_complete' 

@method_decorator(never_cache, name='dispatch')
class RecuperarSenhaView(auth_views.PasswordResetView):
    # Exibe o formulário de solicitação de e-mail e dispara o link seguro gerado pelo Django
    template_name = 'recuperacao_senha/password_reset_form.html'
    email_template_name = 'recuperacao_senha/password_reset_email.html'
    form_class = FormularioRecuperacao

    def form_valid(self, form):
        email = form.cleaned_data.get('email').strip().lower() 
        ip = obter_ip(self.request)


        # gera hash do e-mail e valida os limites por IP e por e-mail no cache
        chave_email = hashlib.sha256(email.encode()).hexdigest()
        if (_estourou_limite(f"recuperacao:ip:{ip}", LIMITE_POR_IP)
                or _estourou_limite(f"recuperacao:email:{chave_email}", LIMITE_POR_EMAIL)):
            logger.warning(f"BLOQUEIO: limite de pedidos de recuperação atingido (ip={ip})")
            form.add_error(None, "Muitos pedidos em pouco tempo. Tente novamente mais tarde.")
            return self.render_to_response(self.get_context_data(form=form), status=429)


        logger.info(f"TENTATIVA: solicitação de recuperação de senha (e-mail={_mascarar_email(email)}, ip={ip})")

        # Tenta enviar o e-mail de recuperação, capturando falhas de conexão SMTP ou de rede
        try: 
            return super().form_valid(form)
        except (smtplib.SMTPException, OSError) as erro:
            logger.error(f"FALHA: não foi possível enviar o e-mail de recuperação ({type(erro).__name__})")
            return redirect(self.get_success_url())
    

@method_decorator(never_cache, name='dispatch')
class RecuperarSenhaEnviadaView(auth_views.PasswordResetDoneView):
    # mostra essa tela depois que o forms e envado
    # aparece igual mesmo se o e-mail não existir no sistema
    template_name = 'recuperacao_senha/password_reset_done.html'

@method_decorator(never_cache, name='dispatch')
class ConfirmarNovaSenhaView(auth_views.PasswordResetConfirmView):
    # essa tela acesso pelo link do e-mail, mas antes mostra o forms de nova senha
    #  e o django verifica se o token é valido ainda
    template_name = 'recuperacao_senha/password_reset_confirm.html'

    def form_valid(self, form):
        
        usuario = form.user

        # # reseta os bloqueios e contadores de falha de login após redefinir a senha com sucesso
        usuario.tentativas_login_falha = 0 
        usuario.bloqueio_ate = None

        
        resposta = super().form_valid(form)
        logger.info(f"SUCESSO: senha redefinida pelo link do e-mail (usuario_id={usuario.pk}, ip={obter_ip(self.request)})")
        return resposta


@method_decorator(never_cache, name='dispatch')
class RecuperacaoConcluidaView(auth_views.PasswordResetCompleteView):
    # essa é a tela final, mostra depois que a senha nova já foi salva no banco
    template_name = 'recuperacao_senha/password_reset_complete.html'