from django.apps import apps
from django.core.management.base import BaseCommand
from alunos.fields import CampoCriptografado

class Command(BaseCommand):
    help = 'Recifra todos os campos criptografados com a chave atual (CHAVE_CRIPTOGRAFIA)'

    def handle(self, *args, **opcoes):
        total = 0
        erros = 0
        
        for modelo in apps.get_models():
            for campo in modelo._meta.get_fields():
                if not isinstance(campo, CampoCriptografado):
                    continue
                
                # Pegamos apenas os IDs e o campo específico para evitar carregar o objeto inteiro se houver erro de decifragem
                for pk in modelo.objects.exclude(**{f'{campo.name}__isnull': True}).values_list('pk', flat=True):
                    try:
                        # Busca o objeto individualmente de forma segura
                        objeto = modelo.objects.get(pk=pk)
                        valor_atual = getattr(objeto, campo.name)
                        
                        # Regrava o valor para forçar a criptografia com a nova chave
                        modelo.objects.filter(pk=pk).update(
                            **{campo.name: valor_atual}
                        )
                        total += 1
                    except Exception as e:
                        erros += 1
                        self.stdout.write(
                            self.style.WARNING(f"Não foi possível recifrar ID {pk} no model {modelo.__name__} ({campo.name}): {e}")
                        )

        self.stdout.write(self.style.SUCCESS(f'Processo finalizado: {total} valores recifrados com sucesso. ({erros} erros ignorados).'))