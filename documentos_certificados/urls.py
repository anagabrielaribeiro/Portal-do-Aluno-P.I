from django.urls import path
from . import views

urlpatterns = [
    path('meus-documentos/', views.meus_documentos, name='meus_documentos'),
    path('solicitar/', views.nova_solicitacao, name='nova_solicitacao_documento'),
    path('certificados/', views.meus_certificados, name='certificados'),
    path('gerar-declaracao/', views.gerar_declaracao_matricula, name='gerar_declaracao'),
]