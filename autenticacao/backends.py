from django.contrib.auth.backends import ModelBackend
from .models import Usuario


class EmailBackend(ModelBackend):
    # Backend customizado que autentica só pelo email, bloqueando o username
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # busca o usuário pelo campo email, usando o valor recebido no parâmetro username
            usuario = Usuario.objects.get(email=username)
        except Usuario.DoesNotExist:
            # não achou ninguém com esse email: autenticação falha
            return None

        # confere se a senha digitada bate com o hash salvo no banco
        if usuario.check_password(password):
            return usuario  # senha certa: retorna o usuário autenticado
        return None  # senha errada: autenticação falha