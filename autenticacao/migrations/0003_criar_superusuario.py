from django.db import migrations
from django.contrib.auth.hashers import make_password

# essa função só será executada quando rodar o migration
def criar_superusuario(apps, schema_editor):
    Usuario = apps.get_model('autenticacao', 'Usuario')

    #Cria o registro do superusuariono banco, com o nome e senha criptografada
    Usuario.objects.create(
        username='Professor.Teste',
        email='professor.teste@portalaluno.com',   # necessário pro recuperação de senha encontrar o usuário
        password=make_password('PortalPI@2026'),
        is_staff=True, # acesso ao painel administrativo
        is_superuser=True, # recebe todas as permissões do sistema
        is_active=True, # deixa a conta ativa
    )

# função só será executada caso a migration seja revertida
def remover_superusuario(apps, schema_editor):
    Usuario = apps.get_model('autenticacao', 'Usuario')
    Usuario.objects.filter(username='Professor.Teste').delete() # remove o usuario criado caso a migration seja desfeita 

# classe que define a migration 
class Migration(migrations.Migration):

    dependencies = [
        ('autenticacao', '0002_usuario_chave_2fa'), # sera executada depois da 0002
    ]

    operations = [
        migrations.RunPython(criar_superusuario, remover_superusuario), # executa o que está na primeira função ao aplicar, e a segunda função ao reverter a migration
    ]