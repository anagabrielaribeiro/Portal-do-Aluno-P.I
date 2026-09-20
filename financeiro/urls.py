from django.urls import path
from . import views

urlpatterns = [
    path('', views.financeiro, name='financeiro'),
    # essa e a unica rota do app, mostra a tela de demonstrativo financeiro
]