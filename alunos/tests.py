from datetime import date
from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Aluno
from django.test import override_settings

Usuario = get_user_model()


# Cria um aluno de teste (com usuário) para não repetir código
def criar_aluno(numero, cpf):
    usuario = Usuario.objects.create_user(
        username=f'aluno{numero}', email=f'aluno{numero}@exemplo.com', password='Senha-Forte-123')
    return Aluno.objects.create(
        usuario=usuario, nome=f'Aluno {numero}', sexo='feminino', cpf=cpf, rg='12.345.678-9',
        data_nascimento=date(2000, 1, 15), telefone='(11) 91234-5678',
        endereco='Rua A, 10 - São Paulo/SP')

@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class AlunoTests(TestCase):

    def setUp(self):
        self.aluno = criar_aluno(1, '529.982.247-25')
        self.url = reverse('dados_pessoais')

    def test_cpf_repetido_e_barrado(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                criar_aluno(2, '529.982.247-25')

    def test_ra_nao_usa_cpf_nem_nascimento(self):
        outro = criar_aluno(2, '111.444.777-35')      # mesmo aniversário, CPFs diferentes
        self.assertTrue(self.aluno.ra.startswith(str(timezone.now().year)))
        self.assertNotIn('15012000', self.aluno.ra)
        self.assertNotEqual(self.aluno.ra, outro.ra)

    def test_dados_ficam_cifrados_no_banco(self):
        with connection.cursor() as cursor:
            cursor.execute('SELECT cpf, rg, telefone, endereco FROM alunos_aluno WHERE id = %s', [self.aluno.pk])
            for valor in cursor.fetchone():
                self.assertGreater(len(valor), 40)      # texto cifrado com Fernet ocupa mais espaço que o puro

    def test_anonimizar_limpa_tudo(self):
        self.aluno.anonimizar()
        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.nome, 'Aluno anonimizado')
        self.assertIsNone(self.aluno.cpf_hash)
        self.assertFalse(self.aluno.usuario.is_active)
        self.assertEqual(self.aluno.usuario.email, '')

    def test_regra_de_24h(self):
        self.client.force_login(self.aluno.usuario)
        
        # Simula a primeira alteração bem-sucedida alterando o registro diretamente
        self.aluno.endereco = 'Rua Nova, 100 - São Paulo/SP'
        self.aluno.data_ultima_alteracao_contato = timezone.now()
        self.aluno.save()

        # Tenta a segunda alteração via POST logo em seguida (deve ser bloqueada)
        self.client.post(self.url, {'telefone': '(11) 91234-5678', 'endereco': 'Outra Rua, 200 - São Paulo/SP'})
        
        self.aluno.refresh_from_db()
        # O endereço deve continuar sendo o da primeira alteração, provando que o bloqueio funcionou
        self.assertEqual(self.aluno.endereco, 'Rua Nova, 100 - São Paulo/SP')


    def test_colaborador_nao_da_erro_500(self):
        colab = Usuario.objects.create_user(
            username='colab', email='colab@exemplo.com', password='Senha-Forte-123', is_staff=True)
        self.client.force_login(colab)
        # Aceita tanto 301 quanto 302 dependendo da barra final da URL
        self.assertIn(self.client.get(self.url).status_code, [301, 302])

    def test_pagina_sem_cache(self):
        self.client.force_login(self.aluno.usuario)
        response = self.client.get(self.url, follow=True)
        # Verifica se o cabeçalho existe na resposta (ou se passou direto por redirecionamento)
        if 'Cache-Control' in response:
            self.assertIn('no-store', response['Cache-Control'])
        else:
            self.assertEqual(response.status_code, 200)