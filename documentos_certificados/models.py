from django.db import models

class TipoDocumento(models.TextChoices):
    ATESTADO = 'atestado', 'Atestado de Matrícula'
    HISTORICO = 'historico', 'Histórico Escolar'
    CERTIFICADO = 'certificado', 'Certificado de Conclusão'

class StatusSolicitacao(models.TextChoices):
    ANALISE = 'analise', 'Em análise'
    LIBERADO = 'liberado', 'Liberado'
    RECUSADO = 'recusado', 'Recusado'

class SolicitacaoDocumento(models.Model):
    aluno = models.ForeignKey('alunos.Aluno', on_delete=models.CASCADE, related_name='documentos_solicitados')
    tipo = models.CharField(max_length=20, choices=TipoDocumento.choices)
    status = models.CharField(max_length=20, choices=StatusSolicitacao.choices, default=StatusSolicitacao.ANALISE)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    # O arquivo só é gerado e preenchido quando o status muda para Liberado
    arquivo_gerado = models.FileField(upload_to='documentos_emitidos/', null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.aluno.nome} ({self.get_status_display()})"

class Certificado(models.Model):
    # Relaciona o certificado ao aluno
    aluno = models.ForeignKey(
        'alunos.Aluno', on_delete=models.CASCADE, related_name='certificados'
    )
    
    titulo = models.CharField(max_length=200, help_text="Ex: Curso de Python Avançado")
    descricao = models.TextField(blank=True, null=True, help_text="Detalhes ou carga horária do evento")
    data = models.DateField(help_text="Data de conclusão ou do evento")
    arquivo = models.FileField(upload_to='certificados/')
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.aluno.nome}"