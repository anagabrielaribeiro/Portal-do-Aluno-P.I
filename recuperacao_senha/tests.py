from django.test import TestCase
from django.core import mail
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from autenticacao.models import Usuario


class RecuperacaoSenhaTests(TestCase):

    def setUp(self):
        # cria um usuario de teste direto no banco de teste do Django
        # (esse banco eh separado, criado e apagado automaticamente a cada rodada de teste,
        # entao nao mexe no banco real do projeto)
        self.usuario = Usuario.objects.create_user(
            username='usuario_teste',
            email='teste@exemplo.com',
            password='SenhaAntiga123'
        )

    def test_formulario_envia_email_para_usuario_existente(self):
        # simula o preenchimento do campo de e-mail e clicando em enviar
        response = self.client.post(reverse('password_reset'), {
            'email': 'teste@exemplo.com'
        })

        # confere se o Django redirecionou pra tela de "e-mail enviado"
        self.assertEqual(response.status_code, 302)

        # confere se exatamente 1 e-mail foi capturado na caixa de teste
        # (django troca o EMAIL_BACKEND pra locmem automaticamente durante os testes,
        # entao aqui nunca sai um e-mail de verdade, nem toca no gmail configurado)
        self.assertEqual(len(mail.outbox), 1)

        email_enviado = mail.outbox[0]
        self.assertIn('teste@exemplo.com', email_enviado.to)

    def test_formulario_nao_envia_email_para_usuario_inexistente(self):
        # o django deve continuar mostrando a mesma tela de sucesso,
        # mas sem enviar nada de verdade, pra nao revelar quais e-mails existem no sistema
        response = self.client.post(reverse('password_reset'), {
            'email': 'naoexiste@exemplo.com'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_fluxo_completo_de_redefinicao_de_senha(self):
        # aqui simula o professor clicando no link que chegou no e-mail e
        # cadastrando uma senha nova

        # gera o mesmo tipo de token e uid que o django coloca no link do e-mail
        uid = urlsafe_base64_encode(force_bytes(self.usuario.pk))
        token = default_token_generator.make_token(self.usuario)

        # primeiro acesso ao link (o django troca o token por um token
        # temporario de sessao na primeira visita, por seguranca)
        url_confirmacao = reverse('password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token,
        })
        response_get = self.client.get(url_confirmacao, follow=True)
        self.assertEqual(response_get.status_code, 200)

        # pega a url final que o django gerou apos validar o token
        url_form_senha_nova = response_get.request['PATH_INFO']

        # envia a senha nova pelo formulario
        response_post = self.client.post(url_form_senha_nova, {
            'new_password1': 'SenhaNova456!',
            'new_password2': 'SenhaNova456!',
        })

        # deve redirecionar pra tela de "recuperacao concluida"
        self.assertEqual(response_post.status_code, 302)

        # confere se a senha realmente mudou no banco
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password('SenhaNova456!'))