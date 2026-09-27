from django.db import migrations


def apagar_aluno_teste(apps, schema_editor):
    from django.db import connection
    Usuario = apps.get_model('autenticacao', 'Usuario')

    try:
        usuario = Usuario.objects.get(username='Professor.Teste')
    except Usuario.DoesNotExist:
        return

    # apaga tudo via SQL puro, sem passar pelo campo cifrado 
    # porque o Django tentar decifrar o CPF em texto puro antes de excluir

    with connection.cursor() as cursor:
        # apaga primeiro os boletos vinculados a esse aluno senão a exclusão
        # do aluno falha, por causa da referência que ainda existiria
        cursor.execute(
            "DELETE FROM financeiro_boleto WHERE aluno_id = ("
            "SELECT id FROM alunos_aluno WHERE usuario_id = %s)",
            [usuario.id]
        )

        # depois apaga o aluno
        cursor.execute("DELETE FROM alunos_aluno WHERE usuario_id = %s", [usuario.id])


def reverter(apps, schema_editor):
    pass  # não recria automaticamente


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0005_alter_aluno_cpf_alter_aluno_endereco_alter_aluno_rg'),
        ('financeiro', '0001_initial'),  # confirma que a tabela de boletos já existe antes de tentar apagar dela
    ]

    operations = [
        migrations.RunPython(apagar_aluno_teste, reverter),
    ]