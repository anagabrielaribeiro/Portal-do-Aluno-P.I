from django.db import models

class Nota(models.Model):
    '''
    Registra a nota de uma aluna, em uma turma, dentro de uma matricula
    
    '''

    TIPOS_CHOICES = [
        ('prova', 'Prova'),
        ('trabalho', 'Trabalho'),
        ('participacao', 'Participação'),
        ('final', 'Nota Final'),
    ]

    # Referencias em string, mesmo motivos das outras models: evitar que o arquivo quebre ao importar junto

    matricula = models.ForeignKey(
        'matriculas.Matricula', on_delete= models.CASCADE, related_name= 'notas'
    )

    turma = models.ForeignKey(
        'calendario_horarios.Turma', on_delete= models.CASCADE, related_name= 'notas'
    )

    nota = models.DecimalField(max_digits= 4, decimal_places= 2)
    tipo = models.CharField(max_length= 30, choices= TIPOS_CHOICES)
    data = models.DateField()

    def __str__(self):
        return f'{self.matricula} - {self.tipo}: {self.nota}'
