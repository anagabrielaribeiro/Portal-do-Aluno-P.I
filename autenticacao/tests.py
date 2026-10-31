from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

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