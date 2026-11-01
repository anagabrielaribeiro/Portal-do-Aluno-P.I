from django.test import TestCase,  override_settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings, RequestFactory
from .models import LogAuditoria, LogAutenticacao
from .views import obter_ip
from django.urls import reverse
from django.db import connection, transaction, DatabaseError
from django.core.cache import cache
from django.contrib.auth.hashers import identify_hasher
from unittest.mock import patch 

User = get_user_model()

class SegurancaAdminTestCase(TestCase):
    def test_admin_login_nao_abre_sessao(self):
        u = User.objects.create_superuser('adm', 'adm@x.com', 'SenhaForte#12345')
        r = self.client.post('/gestao-portal/login/', {'username': 'adm', 'password': 'SenhaForte#12345'})
        self.assertEqual(r.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)



@override_settings(SECURE_SSL_REDIRECT=True)   # liga o redirecionamento, como no site publicado
class ProxyHttpsTests(TestCase):

    # BEHIND_PROXY ligado: o Django confia no cabeçalho do proxy
    @override_settings(SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'))
    def test_cabecalho_https_nao_redireciona(self):
        # simula a Vercel avisando "o pedido original era https"
        resposta = self.client.get('/', HTTP_X_FORWARDED_PROTO='https')
        self.assertNotEqual(resposta.status_code, 301)   # não redireciona, o Django entendeu

    @override_settings(SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'))
    def test_cabecalho_http_redireciona(self):
        # simula o aviso "o pedido original era http"
        resposta = self.client.get('/', HTTP_X_FORWARDED_PROTO='http')
        self.assertEqual(resposta.status_code, 301)                   # redireciona
        self.assertTrue(resposta['Location'].startswith('https://'))  # para https

    # BEHIND_PROXY desligado: o Django ignora o aviso
    @override_settings(SECURE_PROXY_SSL_HEADER=None)
    def test_sem_confiar_no_proxy_redireciona_sempre(self):
        resposta = self.client.get('/', HTTP_X_FORWARDED_PROTO='https')
        self.assertEqual(resposta.status_code, 301)   # mesmo com "https", redireciona: é o loop


class ChaveDoisFatoresCifradaTestCase(TestCase):
    def test_chave_fica_cifrada_no_banco_e_volta_pura_no_orm(self):
        u = User.objects.create_user('a', 'a@x.com', 'SenhaForte#12345')
        u.chave_2fa = 'JBSWY3DPEHPK3PXP'
        u.save()

        with connection.cursor() as c:
            c.execute('SELECT chave_2fa FROM auth_user WHERE id = %s', [u.pk])
            no_banco = c.fetchone()[0]

        self.assertNotEqual(no_banco, 'JBSWY3DPEHPK3PXP')  # o banco não vê a chave pura
        self.assertEqual(User.objects.get(pk=u.pk).chave_2fa, 'JBSWY3DPEHPK3PXP')  # o código lê normal


class LogsImutaveisTestCase(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('b', 'b@x.com', 'SenhaForte#12345')
        self.log = LogAuditoria.objects.create(
            usuario=self.usuario, acao=LogAuditoria.Acao.LOGIN_FALHO, ip_origem='203.0.113.7', detalhes='teste'
        )
        LogAutenticacao.objects.create(usuario=self.usuario, ip='203.0.113.7')

    def test_queryset_nao_altera_nem_apaga(self):
        with self.assertRaises(ValueError):
            LogAuditoria.objects.all().update(detalhes='burlou')
        with self.assertRaises(ValueError):
            LogAuditoria.objects.all().delete()
        with self.assertRaises(ValueError):
            LogAutenticacao.objects.all().update(ip='1.1.1.1')

    def test_sql_direto_e_barrado_pelo_banco(self):
        for sql in (
            'UPDATE autenticacao_logauditoria SET detalhes = \'burlou\'',
            'DELETE FROM autenticacao_logauditoria',
            'UPDATE autenticacao_logautenticacao SET ip = \'1.1.1.1\'',
            'DELETE FROM autenticacao_logautenticacao',
        ):
            with self.assertRaises(DatabaseError):
                with transaction.atomic(), connection.cursor() as c:
                    c.execute(sql)
        self.assertEqual(LogAuditoria.objects.get().detalhes, 'teste')

    def test_apagar_usuario_ainda_funciona_e_o_log_continua(self):
        self.usuario.delete()  # o Django faz SET_NULL no usuario_id do log
        self.assertEqual(LogAuditoria.objects.count(), 1)
        self.assertIsNone(LogAuditoria.objects.get().usuario)


class ObterIpTestCase(TestCase):
    def _req(self, xff=None, addr='10.0.0.1'):
        extra = {'REMOTE_ADDR': addr}
        if xff:
            extra['HTTP_X_FORWARDED_FOR'] = xff
        return RequestFactory().get('/', **extra)

    @override_settings(BEHIND_PROXY=True, PROXIES_CONFIAVEIS=1)
    def test_atras_do_proxy_ignora_ip_forjado_na_frente_da_lista(self):
        self.assertEqual(obter_ip(self._req('1.1.1.1, 203.0.113.7')), '203.0.113.7')

    @override_settings(BEHIND_PROXY=False, PROXIES_CONFIAVEIS=1)
    def test_sem_proxy_o_header_e_ignorado(self):
        self.assertEqual(obter_ip(self._req('1.1.1.1', addr='127.0.0.1')), '127.0.0.1')

    @override_settings(BEHIND_PROXY=True, PROXIES_CONFIAVEIS=1)
    def test_header_invalido_devolve_none(self):
        self.assertIsNone(obter_ip(self._req('<script>')))


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class AdminLogsSomenteLeituraTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('adm2', 'adm2@x.com', 'SenhaForte#12345')
        self.client.force_login(self.admin)
        sessao = self.client.session
        sessao['otp_ok'] = True  # o admin do portal exige o 2FA concluído
        sessao.save()
        self.log = LogAuditoria.objects.create(acao=LogAuditoria.Acao.LOGIN_FALHO, detalhes='teste')

    def test_superusuario_ve_mas_nao_cria_altera_nem_apaga(self):
        lista = reverse('admin:autenticacao_logauditoria_changelist')
        self.assertEqual(self.client.get(lista).status_code, 200)  # consegue ver
        self.assertEqual(self.client.get(reverse('admin:autenticacao_logauditoria_add')).status_code, 403)
        apagar = reverse('admin:autenticacao_logauditoria_delete', args=[self.log.pk])
        self.assertEqual(self.client.post(apagar, {'post': 'yes'}).status_code, 403)
        self.assertEqual(LogAuditoria.objects.count(), 1)


# requisito 1.11: defesa contra força bruta
@override_settings(SECURE_SSL_REDIRECT=False)
class ForcaBrutaTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.usuario = User.objects.create_user('c', 'c@x.com', 'SenhaForte#12345')

    def _errar(self, email='c@x.com', vezes=1):
        for _ in range(vezes):
            self.client.post(reverse('login'), {'username': email, 'password': 'errada'})

    def test_conta_bloqueia_apos_5_falhas(self):
        self._errar(vezes=5)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.esta_bloqueado())

    def test_bloqueio_da_conta_nao_depende_do_cache(self):
        # se o cache cair, o contador por IP some, mas o bloqueio por conta (no banco) continua
        with patch('autenticacao.views.cache') as cache_falso:
            cache_falso.get.side_effect = Exception('cache fora do ar')
            cache_falso.incr.side_effect = Exception('cache fora do ar')
            cache_falso.set.side_effect = Exception('cache fora do ar')
            self._errar(vezes=5)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.esta_bloqueado())

    def test_ip_bloqueado_depois_de_20_falhas(self):
        for i in range(20):
            self._errar(email=f'naoexiste{i}@x.com')  # contas diferentes, mesmo IP
        resposta = self.client.post(reverse('login'), {'username': 'c@x.com', 'password': 'SenhaForte#12345'})
        self.assertEqual(resposta.status_code, 302)
        self.assertNotIn('usuario_pendente_id', self.client.session)  # nem chegou na etapa do 2FA


# requisito 1.2: custo do hash (só passa depois de criar config/hashers.py e trocar no settings)
class HashDaSenhaTestCase(TestCase):
    def test_hash_usa_o_custo_que_definimos(self):
        u = User.objects.create_user('d', 'd@x.com', 'SenhaForte#12345')
        self.assertEqual(u.password.split('$')[0], 'pbkdf2_sha256')
        self.assertEqual(int(u.password.split('$')[1]), 1_500_000)
        self.assertEqual(type(identify_hasher(u.password)).__name__, 'PBKDF2CustoDefinido')