from django.urls import path
from . import views

urlpatterns = [
    path('meu-calendario/', views.meu_calendario, name='meu_calendario'),
]