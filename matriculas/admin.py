from django.contrib import admin
from .models import Curso, Matricula

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'regime', 'modalidade', 'duracao')
    search_fields = ('nome',)

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'curso', 'turma', 'periodo_letivo', 'status', 'data_matricula')
    list_filter = ('status', 'periodo_letivo', 'curso')
    search_fields = ('aluno__nome', 'aluno__ra')