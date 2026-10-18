from django.contrib import admin
from .models import Disciplina, Professor, Sala, Turma, Frequencia

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'carga_horaria')
    search_fields = ('codigo', 'nome')

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email')
    search_fields = ('nome', 'email')

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'bloco', 'capacidade')
    list_filter = ('bloco',)

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'Disciplina', 'Professor', 'Sala', 'periodo')
    list_filter = ('periodo',)
    search_fields = ('codigo',)

@admin.register(Frequencia)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'turma', 'data', 'faltas', 'percentual')
    list_filter = ('turma', 'data')