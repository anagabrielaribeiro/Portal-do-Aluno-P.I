


from django.db import migrations


# cria um aluno fictício vinculado ao usuário de teste, pra ter dados pra testar as telas
def criar_aluno_teste(apps, schema_editor):
    # busca o model dessa forma porque a migration usa uma versão antiga dele
    Usuario = apps.get_model('autenticacao', 'Usuario')
    Aluno = apps.get_model('alunos', 'Aluno')

    # procura o usuário de teste que já existe no banco
    try:
        usuario = Usuario.objects.get(username='Professor.Teste')
    except Usuario.DoesNotExist:
        # se não existir esse usuário, não faz nada e encerra
        return

    # evita criar duplicado se essa migration rodar mais de uma vez
    Aluno.objects.get_or_create(
        usuario=usuario,
        defaults={
            'nome': 'Larissa Almeida Costa',
            'cpf': '987.654.321-00',
            'rg': '32.109.876-5',
            'data_nascimento': '2002-07-19',
            'telefone': '(11) 91234-5678',
            'endereco': 'Rua das Palmeiras, 45 - São Paulo/SP',
            'ra': '99887766554',
        }
    )


# desfaz a criação do aluno de teste, caso alguém precise reverter essa migration
def reverter_aluno_teste(apps, schema_editor):
    Usuario = apps.get_model('autenticacao', 'Usuario')
    Aluno = apps.get_model('alunos', 'Aluno')
    try:
        usuario = Usuario.objects.get(username='Professor.Teste')
        # apaga o aluno vinculado a esse usuário
        Aluno.objects.filter(usuario=usuario).delete()
    except Usuario.DoesNotExist:
        pass


class Migration(migrations.Migration):

    # essa migration depende do Aluno já existir (0001) e do usuário de
    # teste já ter sido criado (0004 de autenticacao)
    dependencies = [
        ('alunos', '0001_initial'),
        ('autenticacao', '0004_atualizar_email_superusuario'),
    ]

    # RunPython executa código Python direto, em vez de criar/alterar tabelas
    operations = [
        migrations.RunPython(criar_aluno_teste, reverter_aluno_teste),
    ]