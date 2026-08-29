from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('ativar-2fa/', views.ativar_2fa_view, name='ativar_2fa'),
    path('verificar-2fa/', views.verificar_2fa_view, name='verificar_2fa'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]