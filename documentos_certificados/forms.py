from django import forms
from .models import Certificado

class CertificadoForm(forms.ModelForm):
    class Meta:
        model = Certificado
        fields = ['titulo', 'descricao', 'data', 'arquivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex: Seminário de Tecnologia'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'Carga horária, organizador, etc...', 'rows': 3}),
            'data': forms.DateInput(attrs={'type': 'date'}),
        }