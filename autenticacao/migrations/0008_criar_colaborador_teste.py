from django.db import migrations


def criar_colaborador_teste(apps, schema_editor):
    Usuario = apps.get_model('autenticacao', 'Usuario')
    Colaborador = apps.get_model('autenticacao', 'Colaborador')

    if not Usuario.objects.filter(username='colaboradorteste').exists():
        usuario = Usuario.objects.create_user(
            username='colaboradorteste',
            password='SenhaTeste@2026',
            email='colaborador.teste@exemplo.com',
            is_staff=True,
        )
        Colaborador.objects.create(usuario=usuario, cargo='Analista')


def remover_colaborador_teste(apps, schema_editor):
    Usuario = apps.get_model('autenticacao', 'Usuario')
    Usuario.objects.filter(username='colaboradorteste').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacao', '0005_logauditoria'),
        ('autenticacao', '0006_colaborador'),
    ]


    operations = [
        migrations.RunPython(criar_colaborador_teste, remover_colaborador_teste),
    ]