from django.urls import path

from . import views


urlpatterns = [
    # Tela onde o usuário fala o e-mail para pedir a recuperação.
    path(
        'password_reset/',
        views.RecuperarSenhaView.as_view(),
        name='password_reset'
    ),

    # Tela de confirmação, avisando que o e-mail foi enviado.
    path(
        'password_reset/done/',
        views.RecuperarSenhaEnviadaView.as_view(),
        name='password_reset_done'
    ),

    # Link que vem no e-mail, contendo o token gerado pelo Django.
    path(
        'reset/<uidb64>/<token>/',
        views.ConfirmarNovaSenhaView.as_view(),
        name='password_reset_confirm'
    ),

    # Tela final, exibida depois que a senha é trocada com sucesso.
    path(
        'reset/done/',
        views.RecuperacaoConcluidaView.as_view(),
        name='password_reset_complete'
    ),
]