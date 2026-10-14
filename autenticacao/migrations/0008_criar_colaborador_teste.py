from django.db import migrations


def criar_colaborador_teste(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacao', '0005_logauditoria'),
        ('autenticacao', '0006_colaborador'),
    ]


    operations = [
        migrations.RunPython(criar_colaborador_teste, migrations.RunPython.noop),
    ]