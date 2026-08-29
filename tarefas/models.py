from django.db import models

class Tarefa(models.Model):
    '''
    Cada tarefa pertence a um aluno especifico, e é utilizado o Foreign Key 
    porque um aluno pode ter mais de uma tarefa.
    
    '''
    aluno = models.ForeignKey(
        'alunos.Aluno', on_delete= models.CASCADE, related_name= 'tarefas'
    )

    titulo = models.CharField(max_length= 120)
    descricao = models.TextField(blank= True, null= True)
    concluida = models.BooleanField(default= False)
    data_criacao = models.DateTimeField(auto_now_add= True) # utilizado para mostrar as tarefas mais recentes com base na data

    def __str__(self):
        return self.titulo
