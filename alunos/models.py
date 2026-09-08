from django.db import models
from django.conf import settings

class Aluno(models.Model):
    """
    Cada aluno está vinculado a uma conta de login, 
    e a relação é OneToOne porque um usuário só pode ter um perfil,
    e um pefil só pode ter um usuário
    """
    # 
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

    @property # só para acessar o método como uma propriedade sem o ()
    # cria a função que mascara o cpf para o visual
    def cpf_mascarado(self):
        numeros = self.cpf.replace('.', '').replace('-', '') # remove o ponto e hífen do cpf
        if len(numeros) != 11:
            return self.cpf
        return f"***.{numeros[3:6]}.{numeros[6:9]}-**"  # esconde os 3 primeiros numeros e os 2 ultimos


    # cria um função para buscar a situação atual do aluno
    @property
    def situacao_atual(self):
        ultima = self.matriculas.order_by('-data_matricula').first() # busca as matriculas ordenadas, e pega a primeira
        return ultima.status if ultima else None # retorna o stats da ultima matricula