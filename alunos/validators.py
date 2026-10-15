import re
from datetime import date
from django.core.exceptions import ValidationError


# Padroniza qualquer CPF digitado para o formato padrão com pontos e traço
def normalizar_cpf(valor):
    numeros = re.sub(r'\D', '', valor or '')        
    if len(numeros) != 11:
        raise ValidationError('O CPF deve ter 11 dígitos.')
    return f'{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}'


# tamanho diferente de 11 ou se todos os números forem iguais ele barra
def validar_cpf(valor):
    numeros = re.sub(r'\D', '', valor or '')

    if len(numeros) != 11 or numeros == numeros[0] * 11:
        raise ValidationError('CPF inválido.')

    for posicao in (9, 10):          # confere o 1º dígito verificador e depois o 2º
        soma = sum(int(numeros[i]) * (posicao + 1 - i) for i in range(posicao))
        digito = (soma * 10) % 11 % 10
        if digito != int(numeros[posicao]):
            raise ValidationError('CPF inválido.')


# valida se a data de nascimento faz sentido no mundo real.
def validar_data_nascimento(valor):
    if valor >= date.today():
        raise ValidationError('A data de nascimento deve estar no passado.')
    if valor.year < 1900:
        raise ValidationError('Data de nascimento inválida.')