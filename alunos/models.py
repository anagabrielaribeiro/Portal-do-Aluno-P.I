from django.db import models
from django.conf import settings

class Aluno(models.Model):
    """
    Cada aluno está vinculado a uma conta de login, 
    e a relação é OneToOne porque um usuário só pode ter um perfil,
    e um pefil só pode ter um usuário
    """

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete = models.CASCADE, # Cascade serve para se caso apagar o usuário, apaga o aluno tambem.
        related_name='aluno', 
        help_text='Conta de login vinculada ao aluno'
    )

    nome = models.CharField(max_length=120)
    cpf = models.CharField(max_length=14, unique=True) # unique para que o cpf não se repita entre alunos diferentes
    rg = models.CharField(max_length=20)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=255)
    ra = models.CharField(max_length= 20, unique= True, help_text='Registro academco')

    def __str__(self):
        return self.nome
