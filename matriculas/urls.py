from django.urls import path
from . import views

urlpatterns = [
    path('minhas-matriculas/', views.minhas_matriculas, name='minhas_matriculas'),
]
