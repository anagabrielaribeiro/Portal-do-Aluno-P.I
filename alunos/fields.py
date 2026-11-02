from cryptography.fernet import Fernet, MultiFernet  
from django.conf import settings
from django.db import models
from django.core.exceptions import ImproperlyConfigured


if not settings.CHAVE_CRIPTOGRAFIA:
    raise ImproperlyConfigured('Defina a variável de ambiente CHAVE_CRIPTOGRAFIA')

# Configura o MultiFernet unindo a chave atual com as chaves antigas do settings
fernet = MultiFernet(
    [Fernet(settings.CHAVE_CRIPTOGRAFIA)] + [Fernet(chave) for chave in getattr(settings, 'CHAVES_CRIPTOGRAFIA_ANTIGAS', [])]
)
class CampoCriptografado(models.CharField):
    # campo de texto que cifra antes de salvar e decifra depois de ler

     # chamado pelo Django antes de gravar no banco
    def get_prep_value(self, value):
        if value is None: # se o campo estiver vazio não tem o que cifrar
            return value
        return fernet.encrypt(value.encode()).decode()  # Transforma o texto em bytes, cifra com a chave, e converte de volta pra texto


        # Chamado pelo Django ao ler o valor do banco
    def from_db_value(self, value, expression, connection):
        if value is None: # Se não veio nada do banco, não tem o que decifrar
            return value
        return fernet.decrypt(value.encode()).decode() # Transforma o texto em bytes, cifra com a chave, e converte de volta pra texto