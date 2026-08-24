from django.db import models

class Disciplina(models.Model):
    nome = models.CharField(max_length= 20)
    codigo = models.CharField(max_length= 20, unique= True) # -> codigo unico para identificação da disciplina (ex: Portugues01)
    carga_horaria = models.PositiveIntegerField(help_text= 'Carga horária em horas')

    def __str__(self):
        return self.nome


class Professor(models.Model):
    '''
    Os professores são cadastrados direto no codigo/admin,
    sem tela para administração (possivel implementação futura)
    
    '''
    nome = models.CharField(max_length= 120)
    email = models.EmailField(max_length= 120, unique= True)

    def __str__(self):
        return self.nome


class Sala(models.Model):
    numero = models.CharField(max_length= 10)
    bloco = models.CharField(max_length= 20)
    capacidade = models.PositiveIntegerField()

    def __str__(self):
        return f'Sala {self.numero} - Bloco {self.bloco}'


class Turma(models.Model):
    '''
    Turma é a união da Disciplina, Professor e Sala

    Usamos o on_delete=Protect para impedir que se caso apague uma sala, Professor
    ou Disciplina que já tenha uma turma vinculada, para não perder o histórico.
    
    '''

    Disciplina = models.ForeignKey(
        Disciplina, on_delete= models.PROTECT, related_name= 'turmas'
    )

    Professor = models.ForeignKey(
        Professor, on_delete= models.PROTECT, related_name= 'turmas'
    )

    Sala = models.ForeignKey(
        Sala, on_delete= models.PROTECT, related_name= 'turmas'
    )

    codigo = models.CharField(max_length= 20, unique= True)
    periodo = models.CharField(max_length= 20, help_text= "Ex: 2026.1")

    def __str__(self):
        return self.codigo


class Frequencia(models.Model):
    '''
    Registra a frequencia do aluno em uma turma. 
    A Foreing Key de Matricula usa referencia em texto (String) em vez de importar direto
    porque calendario_horarios e matriculas dependem um do outro, e se importassem normal,
    um dos arquivos iam quebrar na hora de carregar. 
    
    '''
    #o related_name permite para fazer por exemplo tuma.frequencia.all() 
    # para listar todas as frequencias registradas daquela turma
    matricula = models.ForeignKey(
        'matriculas.Matricula', on_delete = models.CASCADE, related_name= 'frequencias'
    )

    turma = models.ForeignKey(
        Turma, on_delete = models.CASCADE, related_name= 'frequencias'
    )

    faltas = models.PositiveIntegerField(default= 0)
    percentual = models.DecimalField(max_digits= 5, decimal_places= 2)
    data = models.DateField()

    def __str__(self):
        return f'Frequencia {self.matricula} - {self.data}'

    