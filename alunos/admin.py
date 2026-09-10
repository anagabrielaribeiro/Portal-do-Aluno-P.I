from django.contrib import admin
from .models import Aluno
# ferramente interna da instituição usa pra criar, editar e gerecianr dados

# classe que configura como o Aluno aparece dentro do admin
class AlunoAdmin(admin.ModelAdmin):

    # list_display define quais colunas aparecem na listagem de alunos dentro do admin
    # sem isso, o admin mostra só "Aluno object (1)", ilegível
    list_display = ('nome', 'cpf_mascarado', 'situacao_atual')

    # actions é a lista de ações que aparecem no menu suspenso acima da tabela,
    # disponíveis quando você marca um ou mais alunos com o checkbox
    actions = ['anonimizar_aluno']

    # @admin.action define o texto que aparece no menu suspenso pra essa ação
    @admin.action(description='Anonimizar dados pessoais do aluno')
    def anonimizar_aluno(self, request, queryset): # queryset contém todos os alunos que foram marcados no checkbox da lista
        
        # o for percorre cada um, então dá pra anonimizar vários de uma vez
        for aluno in queryset:
            # sobrescreve o dado no banco 
            aluno.nome = 'Aluno anonimizado'
            aluno.cpf = '***.***.***-**'
            aluno.dados_anonimizados = True  # marca que esse aluno já passou pelo processo
            aluno.save()  # grava as mudanças no banco


# admin.site.register conecta o model Aluno à classe AlunoAdmin acima deixando aparecer
admin.site.register(Aluno, AlunoAdmin)
