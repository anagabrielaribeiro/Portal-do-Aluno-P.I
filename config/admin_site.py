from django.contrib import admin
from django.shortcuts import redirect
# cria uma subclasse personalizada do painel administrativo padrão do Django para passar pela segurança do colaborador

class PortalAdminSite(admin.AdminSite):
    def has_permission(self, request):
        # além de staff ativo, exige que o 2FA tenha sido concluído nesta sessão
        return super().has_permission(request) and request.session.get('otp_ok') is True

    def login(self, request, extra_context=None):
        # a tela de login do admin não autentica mais ninguém
        return redirect('login_colaborador')