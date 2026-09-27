from django.db import migrations
import os


def atualizar_senha_professor_teste(apps, schema_editor):
    from django.contrib.auth.hashers import make_password
    Usuario = apps.get_model('autenticacao', 'Usuario')

    senha_nova = os.getenv('SENHA_PROFESSOR_TESTE')
    if not senha_nova:
        # se a variável não existir no .env, não faz nada 
        return

    Usuario.objects.filter(username='Professor.Teste').update(password=make_password(senha_nova))


def reverter(apps, schema_editor):
    pass  # não precisa reverter, é só uma atualização de senha


class Migration(migrations.Migration):

    dependencies = [ # essa migration roda depois da última já criada no app
        ('autenticacao', '0009_merge_20260920_2320'),
    ]

    operations = [
        migrations.RunPython(atualizar_senha_professor_teste, reverter),
    ]