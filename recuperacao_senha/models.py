from django.db import models

# A recuperação de senha usa o próprio Usuario que já existe na app autenticacao (via AUTH_USER_MODEL), 
# então não precisamos criar nenhum model.