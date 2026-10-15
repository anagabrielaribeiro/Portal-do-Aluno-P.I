from django.contrib.auth.backends import ModelBackend
from .models import Usuario


class EmailBackend(ModelBackend):
    # Backend customizado que autentica só pelo email, bloqueando o username
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        
        # busca insensivel a maiúsculas/minúsculas
        # [:2] busca no máximo dois
        usuarios = list(Usuario.objects.filter(email__iexact=username.strip())[:2])


        # 0 é não existe, 2 é email duplicado, os dois casos recusam sem o erro 500
        if len(usuarios) != 1:
            return None

        usuario = usuario.first()

        # confere se a senha digitada bate com o hash salvo no banco, e se conta é ativa
        if usuario.check_password(password) and usuario.is_active:
            return usuario  
        return None  