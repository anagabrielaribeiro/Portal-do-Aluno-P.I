from django.db import migrations

# essa função atualiza o email do superusuario de teste que ja existe,
# trocando o dominio ficticio por um gmail real criado so pra receber
# os e-mails de recuperacao de senha durante os testes/demonstracao
def atualizar_email_superusuario(apps, schema_editor):
    Usuario = apps.get_model('autenticacao', 'Usuario')
    Usuario.objects.filter(username='Professor.Teste').update(
        email='professorteste.portalpi@gmail.com'
    )

# reverte pro email antigo, caso a migration seja desfeita
def reverter_email_superusuario(apps, schema_editor):
    Usuario = apps.get_model('autenticacao', 'Usuario')
    Usuario.objects.filter(username='Professor.Teste').update(
        email='professor.teste@portalaluno.com'
    )

class Migration(migrations.Migration):

    dependencies = [
        ('autenticacao', '0003_criar_superusuario'), # roda depois da criacao do superusuario
    ]

    operations = [
        migrations.RunPython(atualizar_email_superusuario, reverter_email_superusuario),
    ]
