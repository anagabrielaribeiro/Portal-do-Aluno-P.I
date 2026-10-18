from django.contrib import admin
from .models import Nota

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'turma', 'tipo', 'nota', 'data')
    list_filter = ('tipo', 'turma')