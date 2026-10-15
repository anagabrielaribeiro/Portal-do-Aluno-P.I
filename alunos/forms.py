from django import forms
from .models import Aluno
import re

# Fomulario de edição de contato do aluno
class AlunoContatoForm(forms.ModelForm):

    class Meta:
        model = Aluno 
        fields = ['telefone', 'endereco'] # só esses dois campos aparecer e podem ser editados

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone','')
        numeros = re.sub(r'\D', '', telefone) #re.sub remove tudo o que não for número

        if len(numeros) <10:
            raise forms.ValidationError('Informe um número de telefone valido com DDD')
        
        return telefone
    
    def clean_endereco(self):
        endereco = self.cleaned_data.get('endereco', '')

        if len(endereco.strip()) < 5:
            raise forms.ValidationError('Informe um endereço válido')

        return endereco