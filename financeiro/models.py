from django.db import models

class Boleto(models.Model):
    
    aluno = models.ForeignKey(
        'alunos.Aluno', on_delete=models.CASCADE, related_name='boletos' # 'alunos.Aluno' em string
    )
     

    mes_referencia = models.CharField(max_length=20)  # ex: "Agosto/2026" um rótulo pra exibir na tabela
    vencimento = models.DateField()  # data real de vencimento é pra ordenar os boletos
    valor = models.DecimalField(max_digits=8, decimal_places=2)  
    pago = models.BooleanField(default=False)  # controla se mostra "Pago" ou "Pendente" na tela
    arquivo = models.FileField(upload_to='boletos/')  # guarda o PDF; Django salva o arquivo físico em media/boletos/ e só a referência no banco

    class Meta:
        ordering = ['vencimento']
        # já entrega os boletos ordenados por data sempre que a gente fizer Boleto.objects.filter

    def __str__(self):
        return f'{self.aluno} - {self.mes_referencia}'
        # aparece assim na listagem do Django Admin, facilita achar o boleto certo pra editar
