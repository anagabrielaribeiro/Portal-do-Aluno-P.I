from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from alunos.models import Aluno
from .models import Boleto

Usuario = get_user_model()  # pega o model de usuário do projeto


def criar_colaborador(nome):
    # usuário sem aluno vinculado, como um colaborador
    return Usuario.objects.create_user(
        username=nome, email=f'{nome}@teste.com', password='senha123'  # AJUSTE: se o seu Usuario pedir outros campos
    )


def criar_aluno(nome, cpf):
    # cria o usuário de login e o aluno ligado a ele
    usuario = criar_colaborador(nome)
    aluno = Aluno.objects.create(
        usuario=usuario,
        nome=nome,
        sexo=Aluno.Sexo.FEMININO,
        cpf=cpf,  # cada aluno precisa de um cpf diferente (o cpf_hash é único)
        rg='123456789',
        data_nascimento=date(2000, 1, 1),
        telefone='11999999999',
        endereco='Rua Teste, 100',
    )  # o ra e o cpf_hash são gerados sozinhos no save
    return usuario, aluno


def criar_boleto(aluno):
    # cria um boleto de teste para o aluno
    return Boleto.objects.create(
        aluno=aluno,
        mes_referencia='10/2026',  # AJUSTE: se for DateField, use date(2026, 10, 1)
        vencimento=date.today() + timedelta(days=5),
        valor=Decimal('500.00'),
        pago=False,
    )


@override_settings(
    CHAVE_HASH_CPF='chave-so-de-teste',  # o save do Aluno exige essa chave
    SECURE_SSL_REDIRECT=False,           # nos testes não redireciona para https
)
class FinanceiroTests(TestCase):

    def setUp(self):
        # roda antes de cada teste: cria dois alunos, cada um com um boleto
        self.usuario1, self.aluno1 = criar_aluno('aluno1', '111.444.777-35')
        self.usuario2, self.aluno2 = criar_aluno('aluno2', '529.982.247-25')
        self.boleto1 = criar_boleto(self.aluno1)
        self.boleto2 = criar_boleto(self.aluno2)

    def test_sem_login_redireciona(self):
        # quem não está logado deve ser mandado para o login (302)
        resposta = self.client.get(reverse('financeiro'))  # AJUSTE: nome da url da tela do financeiro
        self.assertEqual(resposta.status_code, 302)

    def test_colaborador_nao_da_erro_500(self):
        # colaborador não tem aluno vinculado: a tela abre sem boletos
        colaborador = criar_colaborador('colab')
        self.client.force_login(colaborador)  # entra sem precisar digitar senha
        resposta = self.client.get(reverse('financeiro'))
        self.assertEqual(resposta.status_code, 200)

    def test_aluno_ve_so_os_proprios_boletos(self):
        self.client.force_login(self.usuario1)
        resposta = self.client.get(reverse('financeiro'))
        self.assertEqual(resposta.status_code, 200)
        boletos = list(resposta.context['boletos'])  # lista enviada ao template
        self.assertIn(self.boleto1, boletos)
        self.assertNotIn(self.boleto2, boletos)

    def test_aluno_baixa_o_proprio_boleto(self):
        self.client.force_login(self.usuario1)
        resposta = self.client.get(reverse('baixar_boleto', args=[self.boleto1.id]))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta['Content-Type'], 'application/pdf')  # veio um PDF

    def test_aluno_nao_baixa_boleto_de_outro(self):
        self.client.force_login(self.usuario1)
        resposta = self.client.get(reverse('baixar_boleto', args=[self.boleto2.id]))
        self.assertEqual(resposta.status_code, 404)  # boleto de outro aluno dá 404

    def test_colaborador_nao_baixa_boleto(self):
        colaborador = criar_colaborador('colab')
        self.client.force_login(colaborador)
        resposta = self.client.get(reverse('baixar_boleto', args=[self.boleto1.id]))
        self.assertEqual(resposta.status_code, 404)