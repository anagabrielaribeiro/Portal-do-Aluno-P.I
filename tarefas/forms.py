import re 
from django import forms
from djnago.utils.html import strip_tags
from .models import Tarefa


# padrões de tentativas de injeção de SQL
PADRAO_SQL = re.compile(
    r"(--|/\*|\*/"
    r"|;\s*(drop|delete|insert|update|alter|truncate|select)\b"
    r"|\b(drop|truncate|alter)\s+table\b"
    r"|\bdelete\s+from\b"
    r"|\binsert\s+into\b"
    r"|\bunion\s+select\b)",
    re.IGNORECASE,
)


# tira as tags HTML e caracteres de controles, deixando só o texto puro
def limpar_texto(valor):
    valor = strip_tags(valor)
    valor = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", valor) # remove caracter invisíveis 
    return valor.strip()



class TarefaForm(forms.ModelForm):


    class Meta:
        mdoel = Tarefa 
        fields = ['titulo', 'descricao']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Título'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'Descrição'})
        }


    # limpa um texto e recusa se aparecer um comando  sql
    def _texto_seguro(self, campo):
        valor = limpar_texto(self.cleaned_data.get(campo) or '')
        if PADRAO_SQL.search(valor):
            raise forms.ValidationError('O texto contém trechos não permitidos')
        return valor

    # chama o clean_campo ao validar o forms
    def clean_titulo(self):
        valor = self._texto_seguro('titulo')
        #confirma que o titulo não ficou vazio depois da limpeza
        if not valor:
            raise forms.ValidationError('Informe um titulo')
        return valor
    
    def clean_descricao(self):
        return self._texto_seguro('descricao')

# na edição marcar a tarefa como concluida
class TarefaEdicaoForm(TarefaForm):
    
    class Meta(TarefaEdicaoForm.Meta):
        fields = ['titulo', 'descicao', 'concluida']
