from django.urls import path
from . import views

urlpatterns = [
    path('notas-e-faltas/', views.notas_faltas, name='notas_faltas'),
]