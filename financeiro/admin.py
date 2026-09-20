from django.contrib import admin
from .models import Boleto

admin.site.register(Boleto)
# registra o model Boleto no Django Admin, criando automaticamente uma tela de CRUD 
# por aqui que será a onde a secretaria sobe os boletos e marca "pago" quando o aluno pagar