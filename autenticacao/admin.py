from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
from .models import Usuario, LogAutenticacao
from .models import Colaborador

admin.site.register(Usuario, UserAdmin)


@admin.register(LogAutenticacao)
class LogAutenticacaoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'evento', 'ip')  # colunas mostradas na listagem do admin
    readonly_fields = [f.name for f in LogAutenticacao._meta.fields]  # todos os campos ficam somente leitura

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cargo')  # colunas mostradas na listagem do admin
