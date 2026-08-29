from django.db import models

class Curso(models.Model):
    nome = models.CharField(max_length= 120)
    descricao = models.TextField()
    duracao = models.PositiveIntegerField()

    def __str__(self):
        return self.nome

class Matricula(models.Model):
    '''
    Liga um aluno, a um curso e turma. Aluno e Turma us
    
    '''

    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('trancada', 'Trancada'),
        ('concluida', 'Concluida'),
        ('cancelada', 'Cancelada'),
    ]

    aluno = models.ForeignKey(
        'alunos.Aluno', on_delete= models.CASCADE, related_name= 'matriculas'
    )

    curso = models.ForeignKey(
        Curso, on_delete= models.PROTECT, related_name= 'matriculas'
    )

    turma = models.ForeignKey(
        'calendario_horarios.Turma', on_delete= models.PROTECT, related_name= 'matriculas'
    )

    data_matricula = models.DateField(auto_now_add= True)
    status = models.CharField(max_length= 20, choices= STATUS_CHOICES, default= 'ativa')

    def __str__(self):
        return f'{self.aluno} - {self.curso} - ({self.status})'


