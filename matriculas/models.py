from django.db import models

# Modelo Curso
class Curso(models.Model):
    nome = models.CharField(max_length= 120)
    descricao = models.TextField()
    duracao = models.PositiveIntegerField()

    # cria a opção de regimes semestral ou anual 
    class Regime(models.TextChoices):
        SEMESTRAL = 'semestral', 'Semestral'
        ANUAL = 'anual', 'Anual'

    # cria as opções de modalidades, presencial,hibrido ou EAD
    class Modalidade(models.TextChoices):
        PRESENCIAL = 'presencial', 'Presencial'
        EAD = 'ead', 'EAD'
        HIBRIDO = 'hibrido', 'Híbrido'

    # cria o campos de egime, modadlidade e
    regime = models.CharField(max_length=20, choices=Regime.choices, default=Regime.SEMESTRAL)
    modalidade = models.CharField(max_length=20, choices=Modalidade.choices, default=Modalidade.PRESENCIAL)


    def __str__(self):
        return self.nome

    @property # permite acessar a função cmo uma propriedade 
    # cria uma função para gerar automaticamente a sigla do curso, 
    def sigla(self):
        palavras_ignoradas = {'de', 'da', 'do', 'das', 'dos', 'e'}
        palavras = self.nome.split()
        letras = [
            palavra[0].upper() 
            for palavra in palavras 
                if palavra.lower() not in palavras_ignoradas
            ]
        return ''.join(letras)

# cria o modelo da matricula
class Matricula(models.Model):
    '''
    Liga um aluno, a um curso e turma. Aluno e Turma us
    
    '''

    # opções do status da matricula
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('trancada', 'Trancada'),
        ('concluida', 'Concluida'),
        ('cancelada', 'Cancelada'),
    ]

    # cria uma relação entre matricula e o aluno, se o aluno for excluido, exclui também todas as matriculas
    aluno = models.ForeignKey(
        'alunos.Aluno', on_delete= models.CASCADE, related_name= 'matriculas' # permite acessar as matriculas dos alunos usando aluno.matriculas.all()
    )

    # cria uma relação entre matricula e o curso, e impede que o curso seja exluído enquanto existir matriculas 
    curso = models.ForeignKey(
        Curso, on_delete= models.PROTECT, related_name= 'matriculas'
    )

    # cria uma relação entre matricula e a turma, impede que a turma seja exlcuída enquanto existir matricula
    turma = models.ForeignKey(
        'calendario_horarios.Turma', on_delete= models.PROTECT, related_name= 'matriculas'
    )

    # cria um campo para armazenar o período letivo da matricula
    periodo_letivo = models.CharField(
        max_length=6, help_text='Ex: 2026.2'
    )

    # campos da matricula
    data_matricula = models.DateField(auto_now_add= True)
    status = models.CharField(max_length= 20, choices= STATUS_CHOICES, default= 'ativa')


    # Retorna o aluno, o curso e o status da matrícula em um único texto.
    def __str__(self):
        return f'{self.aluno} - {self.curso} - ({self.status})'

    # Cria uma função que vai gerar o código da matrícula
    @property
    def codigo(self):
        ano = self.periodo_letivo.split('.')[0] # pega o período letivo e separa o ano 
        sufixo = self.aluno.ra[-4:] # pega os 4 ultimos caracteres do RA
        return f'{self.curso.sigla}-{ano}-{sufixo}' # usa a sigla do cursocomo prefixo 
