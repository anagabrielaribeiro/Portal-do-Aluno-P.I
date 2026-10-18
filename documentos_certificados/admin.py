from django.contrib import admin
from .models import SolicitacaoDocumento

@admin.register(SolicitacaoDocumento)
class SolicitacaoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'tipo', 'status', 'data_solicitacao')
    list_filter = ('status', 'tipo')
    search_fields = ('aluno__nome', 'aluno__ra')
    
    # A secretaria só edita o status e o arquivo, não altera quem pediu nem o tipo
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('aluno', 'tipo', 'data_solicitacao')
        return ()