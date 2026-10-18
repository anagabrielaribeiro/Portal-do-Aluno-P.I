from django.contrib.admin.apps import AdminConfig
# configura o Django para utilizar a classe de administração customizada 

class PortalAdminConfig(AdminConfig):
    default_site = 'config.admin_site.PortalAdminSite'