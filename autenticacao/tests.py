from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class SegurancaAdminTestCase(TestCase):
    def test_admin_login_nao_abre_sessao(self):
        u = User.objects.create_superuser('adm', 'adm@x.com', 'SenhaForte#12345')
        r = self.client.post('/gestao-portal/login/', {'username': 'adm', 'password': 'SenhaForte#12345'})
        self.assertEqual(r.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)