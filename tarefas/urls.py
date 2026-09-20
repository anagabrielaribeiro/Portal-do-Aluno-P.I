from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_tarefas, name='lista_tarefas'),
    # tela principal, mostra todas as tarefas do aluno
    
    path('nova/', views.criar_tarefa, name='criar_tarefa'),
    # tela de criar uma tarefa nova

    path('<int:pk>/editar/', views.editar_tarefa, name='editar_tarefa'),
    # tela de editar uma tarefa especifica, pk e o id dela na URL

    path('<int:pk>/apagar/', views.apagar_tarefa, name='apagar_tarefa'),
    # apaga a tarefa direto ao acessar essa URL
]