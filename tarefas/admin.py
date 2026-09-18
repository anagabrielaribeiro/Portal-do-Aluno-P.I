from django.contrib import admin
from .models import Tarefa

admin.site.register(Tarefa)
# registra o model Tarefa no Django Admin
# cria uma tela pronta de criar, listar, editar e apagar, sem precisar escrever nada a mais
