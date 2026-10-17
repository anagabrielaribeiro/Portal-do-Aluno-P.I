from django.db import migrations
from datetime import date, timedelta
from alunos.fields import fernet


def criar_dados_teste(apps, schema_editor):
    Usuario = apps.get_model('autenticacao', 'Usuario')
    Aluno = apps.get_model('alunos', 'Aluno')
    Curso = apps.get_model('matriculas', 'Curso')
    Disciplina = apps.get_model('calendario_horarios', 'Disciplina')
    Professor = apps.get_model('calendario_horarios', 'Professor')
    Sala = apps.get_model('calendario_horarios', 'Sala')
    Turma = apps.get_model('calendario_horarios', 'Turma')
    Matricula = apps.get_model('matriculas', 'Matricula')
    Frequencia = apps.get_model('calendario_horarios', 'Frequencia')
    
    # 1. Garante que o usuário de teste existe
    usuario = Usuario.objects.filter(username='Professor.Teste').first()
    if not usuario:
        usuario = Usuario.objects.create_user(
            username='Professor.Teste',
            email='professorteste.portalpi@gmail.com',
            password='Senha-Forte-123',
            is_staff=True,
            is_superuser=True
        )
    
    if usuario.email != 'professorteste.portalpi@gmail.com':
        usuario.email = 'professorteste.portalpi@gmail.com'
        usuario.save(update_fields=['email'])

    # 2. Cria o Aluno usando SQL puro com dados já criptografados
    aluno = Aluno.objects.filter(usuario=usuario).first()
    if not aluno:
        cpf_cifrado = fernet.encrypt('123.456.789-00'.encode()).decode()
        rg_cifrado = fernet.encrypt('12.345.678-9'.encode()).decode()
        telefone_cifrado = fernet.encrypt('(11) 99999-9999'.encode()).decode()
        endereco_cifrado = fernet.encrypt('Rua Teste, 123 - Sao Paulo/SP'.encode()).decode()
        
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO alunos_aluno 
                (usuario_id, nome, sexo, cpf, rg, data_nascimento, telefone, endereco, ra, dados_anonimizados)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    usuario.id,
                    'Aluno de Teste PI',
                    'neutro',
                    cpf_cifrado,
                    rg_cifrado,
                    '2000-01-01',
                    telefone_cifrado,
                    endereco_cifrado,
                    '2026123456',
                    False
                ]
            )
            cursor.execute("SELECT id FROM alunos_aluno WHERE usuario_id = %s", [usuario.id])
            aluno_id = cursor.fetchone()[0]
        aluno = Aluno.objects.get(id=aluno_id)
    
    # 3. Estrutura acadêmica
    curso, _ = Curso.objects.get_or_create(
        nome='Engenharia de Software',
        defaults={'descricao': 'Curso de teste', 'duracao': 10, 'regime': 'semestral', 'modalidade': 'presencial'}
    )
    
    disciplina, _ = Disciplina.objects.get_or_create(
        codigo='ENG001',
        defaults={'nome': 'Projeto Integrador', 'carga_horaria': 80}
    )
    
    prof, _ = Professor.objects.get_or_create(
        email='professor@teste.com',
        defaults={'nome': 'Prof. Teste'}
    )
    
    sala, _ = Sala.objects.get_or_create(
        numero='101',
        defaults={'bloco': 'A', 'capacidade': 40}
    )
    
    turma, _ = Turma.objects.get_or_create(
        codigo='ENG001-2026A',
        defaults={
            'Disciplina': disciplina,
            'Professor': prof,
            'Sala': sala,
            'periodo': '2026.2'
        }
    )
    
    # 4. Matrícula Ativa
    matricula, _ = Matricula.objects.get_or_create(
        aluno=aluno,
        turma=turma,
        defaults={
            'curso': curso,
            'periodo_letivo': '2026.2',
            'status': 'ativa'
        }
    )
    
    # 5. Frequência
    hoje = date.today()
    Frequencia.objects.get_or_create(
        matricula=matricula,
        turma=turma,
        data=hoje - timedelta(days=2),
        defaults={'faltas': 0, 'percentual': 100.00}
    )


def reverter_dados_teste(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('alunos', '0011_alter_aluno_sexo_alter_aluno_usuario'),
        ('matriculas', '0002_curso_modalidade_curso_regime_and_more'),
        ('calendario_horarios', '0002_initial'),
    ]
    
    operations = [
        migrations.RunSQL(
            "ALTER TABLE alunos_aluno ALTER COLUMN cpf TYPE VARCHAR(255)",
            "ALTER TABLE alunos_aluno ALTER COLUMN cpf TYPE VARCHAR(100)"
        ),
        migrations.RunSQL(
            "ALTER TABLE alunos_aluno ALTER COLUMN rg TYPE VARCHAR(255)",
            "ALTER TABLE alunos_aluno ALTER COLUMN rg TYPE VARCHAR(100)"
        ),
        migrations.RunSQL(
            "ALTER TABLE alunos_aluno ALTER COLUMN telefone TYPE VARCHAR(255)",
            "ALTER TABLE alunos_aluno ALTER COLUMN telefone TYPE VARCHAR(20)"
        ),
        migrations.RunSQL(
            "ALTER TABLE alunos_aluno ALTER COLUMN endereco TYPE VARCHAR(2000)",
            "ALTER TABLE alunos_aluno ALTER COLUMN endereco TYPE VARCHAR(400)"
        ),
        migrations.RunPython(criar_dados_teste, reverter_dados_teste),
    ]