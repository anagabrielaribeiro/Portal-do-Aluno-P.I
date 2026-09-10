
import django.db.models.deletion
from django.db import migrations, models

# essa migration é a primeira do app matriculas, cria as tabelas do zero
class Migration(migrations.Migration):

    initial = True

    # precisa que essas tabelas existam antes
    dependencies = [
        ('alunos', '0001_initial'),
        ('calendario_horarios', '0001_initial'),
    ]

    operations = [
        # cria a tabela Curso
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), # id automatico seria a primari key
                ('nome', models.CharField(max_length=120)),
                ('descricao', models.TextField()),
                ('duracao', models.PositiveIntegerField()),
            ],
        ),

        # cria a tabela Matricula
        migrations.CreateModel(
            name='Matricula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_matricula', models.DateField(auto_now_add=True)), # data da matricula, prenchida sozinha na criação
                ('status', models.CharField(choices=[('ativa', 'Ativa'), ('trancada', 'Trancada'), ('concluida', 'Concluida'), ('cancelada', 'Cancelada')], default='ativa', max_length=20)), # situação da matricula
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matriculas', to='alunos.aluno')), #liga a matriula no curso, se caso alun for apagado apaga a matricula
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='matriculas', to='matriculas.curso')), # liga a matricula a curso, impede apagar o curso enquanto tiver matricula
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='matriculas', to='calendario_horarios.turma')), # liga a matricula a uma turma, impede apagar a turma enquanto tiver matricula
            ],
        ),
    ]
