from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
from .models import Usuario, LogAutenticacao
from .models import Colaborador
from .models import LogAuditoria

admin.site.register(Usuario, UserAdmin)


@admin.register(LogAutenticacao)
class LogAutenticacaoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'evento', 'ip')  # colunas mostradas na listagem do admin
    readonly_fields = [f.name for f in LogAutenticacao._meta.fields]  # todos os campos ficam somente leitura

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cargo')  # colunas mostradas na listagem do admin


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'acao', 'risco', 'ip_origem')  # colunas mostradas na listagem
    list_filter = ('acao', 'risco')  # permite filtrar por tipo de ação e nível de risco, útil pra auditoria
    readonly_fields = [f.name for f in LogAuditoria._meta.fields]  # somente leitura, é um log, não deve ser editado
