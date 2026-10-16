from django.urls import path
from . import views

urlpatterns = [
    path('', views.financeiro, name='financeiro'), # tela do financeiro 
    path('boleto/<int:boleto_id>/', views.baixar_boleto, name='baixar_boleto'),  # rota do download
] 