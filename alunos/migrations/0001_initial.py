
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    # primeira migration
    initial = True

    # depende do model de usuário estar pronto antes
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    # lista de operaçõoes 
    operations = [
        #cria a tabela aluno com os campos da model 
        migrations.CreateModel(
            name='Aluno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120)),
                ('cpf', models.CharField(max_length=14, unique=True)),
                ('rg', models.CharField(max_length=20)),
                ('data_nascimento', models.DateField()),
                ('telefone', models.CharField(max_length=20)),
                ('endereco', models.CharField(max_length=255)),
                ('ra', models.CharField(help_text='Registro academco', max_length=20, unique=True)),
                ('usuario', models.OneToOneField(help_text='Conta de login vinculada ao aluno', on_delete=django.db.models.deletion.CASCADE, related_name='aluno', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
