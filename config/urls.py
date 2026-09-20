"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), # tela administrativa que a instituição usa
    path('', include('autenticacao.urls')), #
    path('', include('recuperacao_senha.urls')),
    path('alunos/', include('alunos.urls')),
    path('matriculas/', include('matriculas.urls')),
    path('privacidade/', include('privacidade_lgpd.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('tarefas/', include('tarefas.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# soma essa nova rota a lista de rotas que ja existe
# essa rota faz o Django entregar os arquivos que estao na pasta media 