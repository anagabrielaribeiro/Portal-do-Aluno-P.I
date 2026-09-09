from django import forms
from .models import Aluno


class AlunoContatoForm(forms.ModelForm):
    """
    Formulário de edição de contato do alino, apenas os campos telefone e edereço
    que o aluno pode alterar. Os demais como nome, cpf, rg, ra, sexo e data de nascimento
    fica bloqueado
    """

    # configura o formuario dizen qual model ele vem e quais campos usar
    class Meta:
        model = Aluno # o formulario é baseado no model aluno
        fields = ['telefone', 'endereco'] # só esses dois campos aparecer e podem ser editados