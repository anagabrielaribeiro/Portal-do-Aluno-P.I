from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):

    
    autentificacao_dois_fatores = models.BooleanField(
        default= False,

    )

    tentativas_login_falha = models.PositiveIntegerField(
        default= 0,
        help_text= 'contagem de tentativas de login'
    )

    bloqueio_ate = models.DateTimeField(
        null= True,
        blank= True,
        help_text= 'usuário bloqueado até essa data e hora'
    )

    ultimo_login = models.DateTimeField(
        null= True,
        blank= True,
        help_text= 'registro do último login bem-sucedido'
        )

    ultimo_ip_acesso = models.GenericIPAddressField(
        null= True,
        blank= True,
        help_text= 'IP do último acesso'
    )

    def esta_bloqueado(self): 
        if self.bloqueio_ate:
            return timezone.now() < self.bloqueio_ate
        return False

    def __str__(self):
        return self.username