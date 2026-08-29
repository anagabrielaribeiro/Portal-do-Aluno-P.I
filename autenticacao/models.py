from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# O usuario já vem pronto com username, password, email, firt name, last name
# e todo o sistema de hash da senha pelo django
class Usuario(AbstractUser):

    # seria o 2F, ele guarda se o usuário já configurou ou não
    # começa com o False porque toda conta nova ainda não passou pelo 2f
    autentificacao_dois_fatores = models.BooleanField(
        default= False,

    )

    # quantas vezes seguidas a senha foi digitada errada
    tentativas_login_falha = models.PositiveIntegerField(
        default= 0,
        help_text= 'contagem de tentativas de login'
    )

    # guarda até quando o usuário fica bloqueado, depois de errar demais
    # só é preenchido quando o bloqueio acontece 
    bloqueio_ate = models.DateTimeField(
        null= True,
        blank= True,
        help_text= 'usuário bloqueado até essa data e hora'
    )


    # registra o ultimo login que deu certo
    # o login só conta como completo quando passa pelo 2f
    ultimo_login = models.DateTimeField(
        null= True,
        blank= True,
        help_text= 'registro do último login bem-sucedido'
        )


    # guarda o endereço de ip onde veio o ultimo acesso
    # GenericIPAddressField valida se o valor é um IP de verdade, IPv4 e IPv6
    ultimo_ip_acesso = models.GenericIPAddressField(
        null= True,
        blank= True,
        help_text= 'IP do último acesso'
    )

    # chave secreta usada pela biblioteca pyotp gerar e conferir os 2f
    # ela é criada uma vez só, no login, e fica guardada para usar no proximo
    chave_2fa = models.CharField(
    max_length=32,
    null=True,
    blank=True,
    help_text='chave secreta usada para gerar os códigos do autenticador'
    )

    # esse método responde se o usuario está bloqueado agora
    # se não tiver nenhuma data de bloqueio salva, retorna False 
    #se tiver, compara com o horário atual para ver se o bloqueio já terminou 
    def esta_bloqueado(self): 
        if self.bloqueio_ate:
            return timezone.now() < self.bloqueio_ate
        return False

    def __str__(self):
        return self.username
    