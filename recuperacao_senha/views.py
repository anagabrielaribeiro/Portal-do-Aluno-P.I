import logging
from django.shortcuts import render
from django.contrib.auth import views as auth_views

# Chama o logger configurado no settings.py
logger = logging.getLogger('recuperacao_senha')


# Nota: não precisamos definir "success_url" em nenhuma dessas views. 
# O Django já sabe para onde redirecionar sozinho, porque ele procura automaticamente pelas urls de nome 
# 'password_reset_done' e 'password_reset_complete' 

class RecuperarSenhaView(auth_views.PasswordResetView):
    # mostra o forms pedindo o e-mail e dispara o link de recuperação. 
    # o django já gera o token seguro (com o secret_key) e checa se existe algum usuario com o e-mail
    template_name = 'recuperacao_senha/password_reset_form.html'
    email_template_name = 'recuperacao_senha/password_reset_email.html'

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        logger.info(f"TENTATIVA: Solicitação de recuperação de senha enviada para o e-mail: {email}")
        return super().form_valid(form)


class RecuperarSenhaEnviadaView(auth_views.PasswordResetDoneView):
    # mostra essa tela depois que o forms e envado
    # aparece igual mesmo se o e-mail não existir no sistema
    template_name = 'recuperacao_senha/password_reset_done.html'


class ConfirmarNovaSenhaView(auth_views.PasswordResetConfirmView):
    # essa tela acesso pelo link do e-mail, mas antes mostra o forms de nova senha
    #  e o django verifica se o token é valido ainda
    template_name = 'recuperacao_senha/password_reset_confirm.html'

    def form_valid(self, form):
        logger.info("SUCESSO: Senha redefinida e validada com sucesso pelo token de acesso.")
        return super().form_valid(form)


class RecuperacaoConcluidaView(auth_views.PasswordResetCompleteView):
    # essa é a tela final, mostra depois que a senha nova já foi salva no banco
    template_name = 'recuperacao_senha/password_reset_complete.html'