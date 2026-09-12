from django.contrib import admin
from .models import Consentimento

# registra o Consentimento no admin, pra instituição ver quem aceitou o que
admin.site.register(Consentimento)
