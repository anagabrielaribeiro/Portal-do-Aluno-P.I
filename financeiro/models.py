from django.db import models
from django.conf import settings

class Boleto(models.Model):
    
    aluno = models.ForeignKey(
        'alunos.Aluno', on_delete=models.CASCADE, related_name='boletos' # 'alunos.Aluno' em string
    )

    mes_referencia = models.CharField(max_length=20)  # ex: "Agosto/2026" um rótulo pra exibir na tabela
    vencimento = models.DateField()  # data real de vencimento é pra ordenar os boletos
    valor = models.DecimalField(max_digits=8, decimal_places=2)  
    pago = models.BooleanField(default=False)  # controla se mostra "Pago" ou "Pendente" na tela
    arquivo = models.FileField(upload_to='boletos/')  # guarda o PDF; Django salva o arquivo físico em media/boletos/ e só a referência no banco

class HistoricoPagamento(models.Model):
    # guarda quem mudou o pago de um boleto e quando
    boleto = models.ForeignKey(Boleto, on_delete=models.CASCADE, related_name='historico')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True) # quem alterou 
    pago_anterior = models.BooleanField()
    pago_novo = models.BooleanField()
    data= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data']
        # já entrega os boletos ordenados por data mais recente

    def __str__(self):
        return f'{self.boleto} - {self.data:%d/%m/%Y %H:%M}'
        # aparece assim na listagem do Django Admin, facilita achar o boleto certo pra editar
