from django.db import migrations
import os


def atualizar_contas_teste(apps, schema_editor):
    from django.contrib.auth.hashers import make_password
    Usuario = apps.get_model('autenticacao', 'Usuario')

    # email do Professor.Teste a senha dele já foi corrigida na migration 0010
    email_professor = os.getenv('EMAIL_PROFESSOR_TESTE')
    if email_professor:  # só atualiza se a variável existir no .env, evitando travar quem ainda não configurou
        Usuario.objects.filter(username='Professor.Teste').update(email=email_professor)

    # senha e email do colaboradorteste 
    senha_colaborador = os.getenv('SENHA_COLABORADOR_TESTE')
    email_colaborador = os.getenv('EMAIL_COLABORADOR_TESTE')

    # só segue se a senha estiver definida no .env
    if senha_colaborador: # monta um dicionário com os campos que vão ser atualizados
        campos_colaborador = {'password': make_password(senha_colaborador)}
        if email_colaborador:
            campos_colaborador['email'] = email_colaborador
        Usuario.objects.filter(username='colaboradorteste').update(**campos_colaborador)


def reverter(apps, schema_editor):
    pass  # não precisa reverter, é só uma atualização de dado


class Migration(migrations.Migration):
    # essa migration roda depois da que já corrigiu a senha do professor
    dependencies = [
        ('autenticacao', '0010_atualizar_senha_professor_teste'),
    ]

    operations = [
        migrations.RunPython(atualizar_contas_teste, reverter),
    ]