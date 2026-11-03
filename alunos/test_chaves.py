from io import StringIO

from cryptography.fernet import Fernet, MultiFernet
from django.core.management import call_command
from django.test import TestCase
from unittest.mock import patch

from autenticacao.models import Usuario


class RotacaoDeChavesTests(TestCase):

    # # Gera chaves simuladas para os testes
    def setUp(self):
        self.chave_antiga = Fernet.generate_key().decode()
        self.chave_nova = Fernet.generate_key().decode()

    # cria um usuario teste
    def test_dado_cifrado_com_a_chave_antiga_continua_legivel_apos_a_troca(self):
        usuario = Usuario.objects.create_user('rot1', 'rot1@x.com', 'SenhaForte#12345')

        # o dado e gravdo quando só a chave antiga existia
        with patch('alunos.fields.fernet', MultiFernet([Fernet(self.chave_antiga)])):
            usuario.chave_2fa = 'JBSWY3DPEHPK3PXP'
            usuario.save()

        # a chave nova passa a ser a princial e a antiga fica só para leitura
        nova_lista = MultiFernet([Fernet(self.chave_nova), Fernet(self.chave_antiga)])
        with patch('alunos.fields.fernet', nova_lista):
            self.assertEqual(Usuario.objects.get(pk=usuario.pk).chave_2fa, 'JBSWY3DPEHPK3PXP')

    def test_comando_recifra_com_a_chave_nova_e_a_antiga_pode_ser_aposentada(self):
        # cria outro usuário de teste
        usuario = Usuario.objects.create_user('rot2', 'rot2@x.com', 'SenhaForte#12345')
        antiga = MultiFernet([Fernet(self.chave_antiga)])
        nova_lista = MultiFernet([Fernet(self.chave_nova), Fernet(self.chave_antiga)])
        so_nova = MultiFernet([Fernet(self.chave_nova)])

        # grava o dado com a chave antiga
        with patch('alunos.fields.fernet', antiga):
            usuario.chave_2fa = 'JBSWY3DPEHPK3PXP'
            usuario.save()

        # executa o comando de rotação com as duas chaves ativas le da antiga e grava com a nova
        with patch('alunos.fields.fernet', nova_lista):
            call_command('rotacionar_chaves', stdout=StringIO())

        # depois da rotação a chave antiga não é mais necessária para ler o dado
        with patch('alunos.fields.fernet', so_nova):
            self.assertEqual(Usuario.objects.get(pk=usuario.pk).chave_2fa, 'JBSWY3DPEHPK3PXP')