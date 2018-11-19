from django.apps import AppConfig

class AvtoregionConfig(AppConfig):
    name = 'Avtoregion'
    verbose_name = 'Авторегион (Диспетчер)'
    
    def ready(self):
        from . import signals