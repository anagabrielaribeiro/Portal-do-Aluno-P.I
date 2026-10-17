from django.test import TestCase, RequestFactory, override_settings
import json
from datetime import date
from unittest.mock import patch
from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from alunos.models import Aluno
from autenticacao.models import Usuario
from .mapeamento import DADOS_PESSOAIS, dados_obrigatorios, finalidades_de_consentimento
from .models import Consentimento, SolicitacaoExclusao
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from .context_processors import termos_pendentes

SENHA = 'SenhaTeste@2026'

# configurações só para os testes: chave do hash do CPF, sem redirecionar para https
# e com arquivos estáticos simples 
CONFIG_TESTE = dict(
    CHAVE_HASH_CPF='chave-de-teste',
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)


def criar_aluno(numero, cpf):
    # cria um usuário de login e o aluno ligado a ele
    usuario = Usuario.objects.create_user(
        username=f'aluno{numero}', email=f'aluno{numero}@exemplo.com', password=SENHA
    )
    aluno = Aluno.objects.create(
        usuario=usuario,
        nome=f'Aluno Teste {numero}',
        sexo='feminino',
        cpf=cpf,
        rg='12.345.678-9',
        data_nascimento=date(2000, 1, 1),
        telefone='(11) 91234-5678',
        endereco='Rua Teste, 123',
    )
    return usuario, aluno


@override_settings(**CONFIG_TESTE)
class BaseLGPD(TestCase):
    # prepara dois alunos e um colaborador para os testes das views

    def setUp(self):
        self.usuario, self.aluno = criar_aluno(1, '529.982.247-25')
        self.usuario2, self.aluno2 = criar_aluno(2, '111.444.777-35')
        self.colaborador = Usuario.objects.create_superuser(
            username='colab', email='colab@exemplo.com', password=SENHA
        )
        self.client.force_login(self.usuario)


# mapeamento
class MapeamentoTest(TestCase):

    def test_todo_dado_tem_base_legal(self):
        for dado in DADOS_PESSOAIS:
            self.assertIn('base_legal', dado, dado['campo'])

    def test_consentimento_so_traz_o_que_e_opcional(self):
        finalidades = finalidades_de_consentimento()
        self.assertIn('contato por telefone', finalidades)
        # cpf e notas são obrigação legal, o aluno não escolhe
        self.assertNotIn('matrícula obrigatória por lei', finalidades)
        self.assertNotIn('registro acadêmico obrigatório', finalidades)

    def test_finalidades_sem_repeticao(self):
        finalidades = finalidades_de_consentimento()
        self.assertEqual(len(finalidades), len(set(finalidades)))

    def test_obrigatorios_nao_incluem_consentimento(self):
        for dado in dados_obrigatorios():
            self.assertNotEqual(dado['base_legal'], 'consentimento')


# model
@override_settings(**CONFIG_TESTE)
class ConsentimentoModelTest(TestCase):

    def setUp(self):
        self.usuario, self.aluno = criar_aluno(1, '529.982.247-25')
        self.consentimento = Consentimento.objects.create(
            aluno=self.aluno, finalidade='contato por telefone'
        )

    def test_revogar_marca_aceito_false_e_guarda_a_data(self):
        self.consentimento.revogar()
        self.consentimento.refresh_from_db()
        self.assertFalse(self.consentimento.aceito)
        self.assertIsNotNone(self.consentimento.data_revogacao)

    def test_revogar_duas_vezes_nao_troca_a_data(self):
        self.consentimento.revogar()
        self.consentimento.refresh_from_db()
        primeira_data = self.consentimento.data_revogacao

        self.consentimento.revogar()
        self.consentimento.refresh_from_db()
        self.assertEqual(self.consentimento.data_revogacao, primeira_data)

    def test_revogar_nao_apaga_o_registro(self):
        self.consentimento.revogar()
        self.assertEqual(Consentimento.objects.filter(aluno=self.aluno).count(), 1)

    def test_apagar_aluno_com_consentimento_funciona(self):
        self.aluno.delete()
        self.assertEqual(Consentimento.objects.count(), 0)


# acesso, aceite e revogação
class ConsentimentoViewsTest(BaseLGPD):

    def test_sem_login_vai_para_o_login(self):
        self.client.logout()
        resposta = self.client.get(reverse('meus_consentimentos'))
        self.assertEqual(resposta.status_code, 302)

    def test_colaborador_recebe_403_em_todas_as_views(self):
        self.client.force_login(self.colaborador)
        self.assertEqual(self.client.get(reverse('meus_consentimentos')).status_code, 403)
        views_post = [
            ('aceitar_termos', []),
            ('revogar_consentimento', [1]),
            ('exportar_dados_json', []),
            ('solicitar_exclusao', []),
        ]
        for nome, args in views_post:
            resposta = self.client.post(reverse(nome, args=args))
            self.assertEqual(resposta.status_code, 403, nome)

    def test_popup_aparece_ate_o_aluno_decidir(self):
        # antes de decidir, a página traz o pop-up
        resposta = self.client.get(reverse('meus_consentimentos'))
        self.assertContains(resposta, 'popup-overlay')

        # depois de aceitar, ele some
        self.client.post(reverse('aceitar_termos'))
        resposta = self.client.get(reverse('meus_consentimentos'))
        self.assertNotContains(resposta, 'popup-overlay')

    def test_aceitar_cria_um_consentimento_por_finalidade(self):
        marcadas = finalidades_de_consentimento()
        self.client.post(reverse('aceitar_termos'), {'finalidades': marcadas})
        criadas = Consentimento.objects.filter(aluno=self.aluno)
        self.assertEqual(criadas.count(), len(marcadas))
        self.assertTrue(all(c.aceito for c in criadas))

    def test_recusar_tudo_registra_e_nao_bloqueia(self):
        # envia sem marcar nenhuma caixa
        self.client.post(reverse('aceitar_termos'))
        criadas = Consentimento.objects.filter(aluno=self.aluno)
        self.assertEqual(criadas.count(), len(finalidades_de_consentimento()))
        self.assertTrue(all(not c.aceito for c in criadas))

        # o aluno continua acessando o portal normalmente
        resposta = self.client.get(reverse('meus_consentimentos'))
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, 'popup-overlay')
        
    def test_aceitar_duas_vezes_nao_duplica(self):
        self.client.post(reverse('aceitar_termos'))
        self.client.post(reverse('aceitar_termos'))
        self.assertEqual(
            Consentimento.objects.filter(aluno=self.aluno).count(),
            len(finalidades_de_consentimento()),
        )

    def test_aceitar_por_get_nao_e_permitido(self):
        self.assertEqual(self.client.get(reverse('aceitar_termos')).status_code, 405)

    
    def test_revogar_marca_o_consentimento(self):
        c = Consentimento.objects.create(aluno=self.aluno, finalidade='contato por telefone')
        self.client.post(reverse('revogar_consentimento', args=[c.id]))
        c.refresh_from_db()
        self.assertFalse(c.aceito)
        self.assertIsNotNone(c.data_revogacao)

    def test_revogar_consentimento_de_outro_aluno_da_404(self):
        de_outro = Consentimento.objects.create(aluno=self.aluno2, finalidade='contato por telefone')
        resposta = self.client.post(reverse('revogar_consentimento', args=[de_outro.id]))
        self.assertEqual(resposta.status_code, 404)
        de_outro.refresh_from_db()
        self.assertTrue(de_outro.aceito)  # o consentimento do outro aluno não foi mexido

    def test_revogar_id_que_nao_existe_da_404(self):
        resposta = self.client.post(reverse('revogar_consentimento', args=[99999]))
        self.assertEqual(resposta.status_code, 404)

    def test_revogar_por_get_nao_e_permitido(self):
        c = Consentimento.objects.create(aluno=self.aluno, finalidade='contato por telefone')
        resposta = self.client.get(reverse('revogar_consentimento', args=[c.id]))
        self.assertEqual(resposta.status_code, 405)


# pedido de exclusão
class SolicitarExclusaoTest(BaseLGPD):

    def setUp(self):
        super().setUp()
        self.url = reverse('solicitar_exclusao')

    def test_grava_pedido_e_envia_email(self):
        resposta = self.client.post(self.url)
        self.assertEqual(resposta.status_code, 302)

        pedido = SolicitacaoExclusao.objects.get(aluno=self.aluno)
        self.assertEqual(pedido.status, 'pendente')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['aluno1@exemplo.com'])
        self.assertIn(f'protocolo {pedido.id}', mail.outbox[0].body)

    def test_nao_duplica_pedido_pendente(self):
        self.client.post(self.url)
        self.client.post(self.url)
        self.assertEqual(SolicitacaoExclusao.objects.filter(aluno=self.aluno).count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_aceita_novo_pedido_depois_de_concluido(self):
        self.client.post(self.url)
        SolicitacaoExclusao.objects.filter(aluno=self.aluno).update(status='concluida')
        self.client.post(self.url)
        self.assertEqual(SolicitacaoExclusao.objects.filter(aluno=self.aluno).count(), 2)

    def test_pedido_fica_salvo_se_o_email_falhar(self):
        with patch('privacidade_lgpd.views.send_mail', side_effect=Exception('falhou')):
            resposta = self.client.post(self.url)
        self.assertEqual(resposta.status_code, 302)  # não deu erro 500
        self.assertEqual(SolicitacaoExclusao.objects.filter(aluno=self.aluno).count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_por_get_nao_e_permitido(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)


# exportação
class ExportarDadosTest(BaseLGPD):

    def setUp(self):
        super().setUp()
        self.url = reverse('exportar_dados_json')
        Consentimento.objects.create(aluno=self.aluno, finalidade='contato por telefone')

    def test_por_get_nao_e_permitido(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_senha_errada_nao_exporta(self):
        resposta = self.client.post(self.url, {'senha': 'senha-errada'})
        self.assertEqual(resposta.status_code, 302)
        self.assertNotIn('Content-Disposition', resposta)
        textos = [str(m) for m in get_messages(resposta.wsgi_request)]
        self.assertTrue(any('Senha incorreta' in t for t in textos))

    def test_sem_senha_nao_exporta(self):
        resposta = self.client.post(self.url)
        self.assertEqual(resposta.status_code, 302)
        self.assertNotIn('Content-Disposition', resposta)

    def test_senha_certa_baixa_o_json_completo(self):
        resposta = self.client.post(self.url, {'senha': SENHA})
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('attachment', resposta['Content-Disposition'])
        self.assertIn('no-store', resposta['Cache-Control'])  # never_cache

        dados = json.loads(resposta.content)
        self.assertEqual(dados['identificacao']['cpf'], '529.982.247-25')  # sem máscara
        self.assertEqual(dados['contato']['email'], 'aluno1@exemplo.com')
        self.assertEqual(len(dados['consentimentos']), 1)
        self.assertEqual(dados['vida_academica'], [])
        self.assertIn('acesso', dados)

    def test_nao_exporta_segredos_nem_dados_de_outro_aluno(self):
        resposta = self.client.post(self.url, {'senha': SENHA})
        conteudo = resposta.content.decode()
        self.assertNotIn('chave_2fa', conteudo)
        self.assertNotIn('Aluno Teste 2', conteudo)
        self.assertNotIn('111.444.777-35', conteudo)


# pop-up e sessão
class ContextProcessorTest(BaseLGPD):

    def pedido_de(self, usuario):
        # monta uma requisição de mentira com o usuário e uma sessão vazia
        request = RequestFactory().get('/')
        request.user = usuario
        request.session = SessionStore()
        return request

    def test_colaborador_nao_ve_popup(self):
        request = self.pedido_de(self.colaborador)
        self.assertFalse(termos_pendentes(request)['mostrar_popup'])

    def test_visitante_sem_login_nao_ve_popup(self):
        request = self.pedido_de(AnonymousUser())
        self.assertFalse(termos_pendentes(request)['mostrar_popup'])

    def test_aluno_sem_consentimento_ve_popup(self):
        request = self.pedido_de(self.usuario)
        resultado = termos_pendentes(request)
        self.assertTrue(resultado['mostrar_popup'])
        self.assertEqual(resultado['finalidades'], finalidades_de_consentimento())

    def test_sessao_guarda_que_o_aluno_ja_aceitou(self):
        Consentimento.objects.create(aluno=self.aluno, finalidade='contato por telefone')
        request = self.pedido_de(self.usuario)
        self.assertFalse(termos_pendentes(request)['mostrar_popup'])
        self.assertTrue(request.session.get('termos_aceitos'))

    def test_com_a_sessao_marcada_nao_consulta_o_banco(self):
        request = self.pedido_de(self.usuario)
        request.session['termos_aceitos'] = True
        with self.assertNumQueries(0):  # é o ganho do commit 8
            termos_pendentes(request)