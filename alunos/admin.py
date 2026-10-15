from django.contrib import admin, messages
from autenticacao.models import LogAuditoria
from autenticacao.views import obter_ip
from .models import Aluno


# ferramente interna da instituição usa pra criar, editar e gerecianr dados
# classe que configura como o Aluno aparece dentro do admin
class AlunoAdmin(admin.ModelAdmin):

    list_display = ('nome', 'cpf_mascarado', 'situacao_atual')# list_display define quais colunas aparecem na listagem de alunos dentro do admin
    search_fields = ('nome', 'ra') 
    actions = ['anonimizar_aluno']

    def get_exclude(self, request, obj=None):
        if request.user.is_superuser:
            return None
        return ('cpf', 'rg', 'endereco', 'telefone')


    def get_readonly_fields(self, request, obj=None):
        campos = ['ra', 'cpf_hash', 'dados_anonimizados', 'data_ultima_alteracao_contato']
        if not request.user.is_superuser:
            campos += ['cpf_mascarado', 'rg_mascarado'] # só a versão mascarada
        return campos

    # só usuario cadastra aluno 
    def has_add_permission(self, request):
        return request.user.is_superuser

    # não apaga aluno pelo admin, ou desativa ou anonimiza
    def has_delete_permission(self, request, obj=None):
        return False

    # premissão de anonimizar só superusuario
    def has_anonimizar_permission(self, request):
        return request.user.is_superuser


    # @admin.action define o texto que aparece no menu suspenso pra essa ação
    @admin.action(description='Anonimizar dados pessoais do aluno')
    def anonimizar_aluno(self, request, queryset): 
        
        # anonimiza um aluno por vez
        if queryset.count() != 1:
            self.massage_user(request, 'Selecione apenas um aluno por vez', messages.ERROR)
            return

        aluno = queryset.first()
        if aluno.dados_anonimizados:
            self.message_user(request, 'Este aluno já foi anonimizado', message.WARNING)
            return

        aluno.anonimizar()    

        LogAuditoria.objects.create(
            usuario= request.user,
            acao= LogAuditoria.Acao.ANONIMIZACAO,
            risco= LogAuditoria.Risco.CRITICO,
            ip_origem= obter_ip(request),
            detalhes= f'Aluno id {aluno.pk} anonimizado'
        )

        self;message_user(request, 'Aluno anonimizado com sucesso', message.SUCCESS)