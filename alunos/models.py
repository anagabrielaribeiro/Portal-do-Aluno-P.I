from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Aluno(models.Model):
    """
    Cada aluno está vinculado a uma conta de login, 
    e a relação é OneToOne porque um usuário só pode ter um perfil,
    e um pefil só pode ter um usuário
    """

    # define as opções de sexo
    class Sexo(models.TextChoices):
        FEMININO = 'feminino', 'Feminino'
        MASCULINO = 'masculino', 'Maculino'
        NEUTRO = 'neutro', 'Neutro'


    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete = models.CASCADE, # Cascade serve para se caso apagar o usuário, apaga o aluno tambem.
        related_name='aluno', 
        help_text='Conta de login vinculada ao aluno'
    )

    nome = models.CharField(max_length=120)
    nome_social = models.CharField(max_length=120, blank=True, null=True)# nome social 
    sexo = models.CharField(max_length=10, choices=Sexo.choices) # sexo feminino, masculino ou neutro
    cpf = models.CharField(max_length=14, unique=True) # unique para que o cpf não se repita entre alunos diferentes
    rg = models.CharField(max_length=20)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=255)
    ra = models.CharField(max_length= 20, unique= True, help_text='Registro academco')
    data_ultima_alteracao_contato = models.DateTimeField(null=True, blank=True) # guarda quando foi a ultima vez que telefone/endereço foram alterados


    def __str__(self):
        return self.nome

    # função para gerar o ra com data de nascimento e final do cpf
    def gerar_ra(self):
        data_str = self.data_nascimento.strftime('%d%m%Y') # junta dia, mês e ano sem separador
        cpf_numeros = self.cpf.replace('.','').replace('-','') 
        sufixo_cpf = cpf_numeros[-3:]
        return f'{data_str}{sufixo_cpf}'

    # só gera o ra automaticamente se ainda não tiver definido 
    def save(self, *args, **kwargs):
        if not self.ra:
            self.ra = self.gerar_ra()
        super().save(*args, **kwargs)



    @property # só para acessar o método como uma propriedade sem o ()
    # cria a função que mascara o cpf para o visual
    def cpf_mascarado(self):
        numeros = self.cpf.replace('.', '').replace('-', '') # remove o ponto e hífen do cpf
        if len(numeros) != 11:
            return self.cpf
        return f"***.{numeros[3:6]}.{numeros[6:9]}-**"  # esconde os 3 primeiros numeros e os 2 ultimos

    @property 
    def rg_mascarado(self):
        valor = self.rg # esconde tudo, exceto os 3 ultimos caracteres
        if len(valor) <= 3:
            return valor
        visiveis = valor[-3:]
        ocultos = '*' * (len(valor) -3)
        return f'{ocultos}{visiveis}'


    # mostra o nome social se tiver, se não o nome do rg 
    @property
    def nome_exibicao(self):
        return self.nome_social if self.nome_social else self.nome

    # cria um função para buscar a situação atual do aluno
    @property
    def situacao_atual(self):
        ultima = self.matriculas.order_by('-data_matricula').first() # busca as matriculas ordenadas, e pega a primeira
        return ultima.status if ultima else None # retorna o stats da ultima matricula

    @property
    # se nunca alterou o contato pode editar
    def pode_editar_contato(self):
        if not self.data_ultima_alteracao_contato:
            return True
        limite = self.data_ultima_alteracao_contato + timedelta(days=1) # calcula a data em que completa 1 dia desde a ultima alteração
        return timezone.now() >= limite # só libera para editar se passou do limite 

    
    # função do proxima edição dos dados telefone e endereço
    @property
    def proxima_edicao_disponivel(self):
        if not self.data_ultima_alteracao_contato: # se nunca alterou, não existe data proxima liberação
            return None
        return self.data_ultima_alteracao_contato + timedelta(days=1) # retorna quando a edição libera de novo 