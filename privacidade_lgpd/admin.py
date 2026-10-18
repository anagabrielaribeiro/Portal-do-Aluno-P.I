from django.contrib import admin
from .models import Consentimento, SolicitacaoExclusao

# registra o Consentimento no admin, pra instituição ver quem aceitou o que
admin.site.register(Consentimento)

@admin.register(SolicitacaoExclusao)
class SolicitacaoExclusaoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'data_pedido', 'status') # colunas da lista
    list_filter = ('status',) # filtro para achar pendentes