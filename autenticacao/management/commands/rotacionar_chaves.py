from django.apps import apps
from django.core.management.base import BaseCommand
from alunos.fields import CampoCriptografado


class Command(BaseCommand):
    # Mensagem de ajuda que aparece no terminal ao rodar 'python manage.py rotacionar_chaves --help'
    help = 'Recifra todos os campos criptografados com a chave atual (CHAVE_CRIPTOGRAFIA)'

    def handle(self, *args, **opcoes):
        total = 0

        # procura em todos os models os campos que usam a cifragem
        for modelo in apps.get_models():
            for campo in modelo._meta.get_fields():
                if not isinstance(campo, CampoCriptografado):
                    continue

                for objeto in modelo.objects.exclude(**{f'{campo.name}__isnull': True}):
                    # ler já decifra (com qualquer chave da lista); gravar cifra de novo com a chave atual
                    modelo.objects.filter(pk=objeto.pk).update(**{campo.name: getattr(objeto, campo.name)})
                    total += 1

        self.stdout.write(f'{total} valores recifrados com a chave atual')