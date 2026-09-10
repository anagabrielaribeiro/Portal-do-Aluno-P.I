from django.urls import path
from . import views

urlpatterns = [
    path('dados-pessoais/', views.dados_pessoais, name='dados_pessoais'),
]