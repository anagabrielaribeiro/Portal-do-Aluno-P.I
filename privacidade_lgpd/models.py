# guarda o consentimento do aluno para cada finalidade deuso dos dados dele


from django.db import models
from django.utils import timezone


class Consentimento(models.Model):
    aluno = models.ForeignKey('alunos.Aluno', on_delete=models.CASCADE, related_name='consentimentos') # de qual aluno é esse consentimento
    finalidade = models.CharField(max_length=100)  # pra que serve esse consentimento
    aceito = models.BooleanField(default=True) # o aluno aceitoi ou não
    versao_termo = models.CharField(max_length=10, default='1.0') # qual versão do termo aceitou
    data_registro = models.DateTimeField(auto_now_add=True) # quando o aluno aceitou
    data_revogacao = models.DateTimeField(null=True, blank=True) # quando ele revogou 

    def revogar(self):
        # se já foi recusado, não faz nada, não sobrescreve a data original
        if not self.aceito:
            return
        # não apaga o registro, só marca como não aceito e guarda a data
        self.aceito = False
        self.data_revogacao = timezone.now()
        self.save(update_fields=['aceito', 'data_revogacao'])


# pedidos de exclusão
class SolicitacaoExclusao (models.Model):
    STATUS =[
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
        ('recusada', 'Recusada'),

    ]
    aluno = models.ForeignKey('alunos.Aluno', on_delete=models.CASCADE, related_name='solicitacoes_exclusao')
    data_pedido =models.DateTimeField(auto_now_add=True) # quando o aluno pediu
    status = models.CharField(max_length=10, choices=STATUS, default='pendente') # muda no admin 

