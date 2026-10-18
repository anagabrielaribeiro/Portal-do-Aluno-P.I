from django.urls import path
from . import views

urlpatterns = [
    path('minha-agenda/', views.minha_agenda, name='minha_agenda'),
]