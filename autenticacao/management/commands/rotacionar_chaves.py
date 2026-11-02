from django.apps import apps
from django.core.management.base import BaseCommand
from alunos.fields import CampoCriptografado


class Command(BaseCommand):
    # Mensagem de ajuda que aparece no terminal ao rodar 'python manage.py rotacionar_chaves --help'
    help = 'Recifra todos os campos criptografados com a chave atual (CHAVE_CRIPTOGRAFIA)'

    def handle(self, *args, **opcoes):
        total = 0
        erros = 0 

        # procura em todos os models os campos que usam a cifragem
        for modelo in apps.get_models():
            for campo in modelo._meta.get_fields():
                if not isinstance(campo, CampoCriptografado):
                    continue

                for objeto in modelo.objects.exclude(**{f'{campo.name}__isnull': True}):
                    try:
                        # Tenta ler o campo (decifra) e gravar de novo com a chave atual
                        valor_atual = getattr(objeto, campo.name)
                        modelo.objects.filter(pk=objeto.pk).update(
                            **{campo.name: valor_atual}
                        )
                        total += 1
                    except Exception as e:
                        # Se der erro (ex: InvalidToken por chave antiga ausente), avisa mas não para o comando
                        erros += 1
                        self.stdout.write(
                            self.style.WARNING(f"Não foi possível recifrar ID {objeto.pk} no model {modelo.__name__} ({campo.name}): {e}")
                        )

        self.stdout.write(self.style.SUCCESS(f'Processo finalizado: {total} valores recifrados com sucesso. ({erros} erros ignorados).'))