from django.contrib import admin
from .models import Boleto, HistoricoPagamento


# exibe o istorico de alterações do boleto em tabela, somente leitura
class HistoricoInline(admin.TabularInline):
    
    model = HistoricoPagamento
    extra = 0 
    can_delete = False
    readonly_fields = ('usuario', 'pago_anterior', 'pago_novo', 'data')

    def has_add_permission(self, request, obj=None):
        return False # ninguém cria historico a mão

    
@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    exclude = ('arquivo',) # pdf gera na hora
    list_display = ('aluno', 'mes_referencia', 'vencimento', 'valor', 'pago')
    list_filter = ('pago', 'vencimento')
    inlines = [HistoricoInline]


    def _pode_gerir(self, request):
        # só superusuario
        u = request.user
        return u.is_superuser or u.groups.filter(name='Financeiro').existis()

    
    def has_add_permission(self, request):
        return self._pode_gerir(request) # só quem pode gerir cria boleto

    def has_change_permission(self, request, obj=None):
        return self._pode_gerir(request) # só quem pode gerir altera o boleto

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser # só super usuario apaga

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change) # salva o boleto

        # se for edição e o pago mudou, guarda historic quem mudoi
        if change and 'pago' in form.changed_data:
            HistoricoPagamento.objects.create(
                Boleto=obj,
                usuario=request.user,
                pago_anterior=not obj.pago, 
                pago_novo=obj.pago,
            )