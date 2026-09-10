# rotas da parte de consentimento

from django.urls import path
from . import views

urlpatterns = [
    path('meus-consentimentos/', views.meus_consentimentos, name='meus_consentimentos'), # chama a função meus_consentimentos em views.py
    path('consentimento/<int:consentimento_id>/revogar/', views.revogar_consentimento, name='revogar_consentimento'), # pega o número da URL e manda como parâmetro pra view revogar_consentimento
]