from django.db import migrations
from django.contrib.auth.hashers import make_password

# não cria mais nenhum conta
def criar_superusuario(apps, schema_editor):
    pass



# classe que define a migration 
class Migration(migrations.Migration):

    dependencies = [
        ('autenticacao', '0002_usuario_chave_2fa'), # sera executada depois da 0002
    ]

    operations = [
        migrations.RunPython(criar_superusuario, migrations.RunPython.noop), 
    ]