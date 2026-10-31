from django.contrib.auth.hashers import PBKDF2PasswordHasher


class PBKDF2CustoDefinido(PBKDF2PasswordHasher):
    # número de iterações definido e não herdado da versão do Django
    # a OWASP recomenda no mínimo 600.000 para PBKDF2-HMAC-SHA256 deixamos acima
    iterations = 1_500_000