from django.apps import AppConfig

class GestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion'  # Cambia esto al nombre de tu app

    def ready(self):
        from . import signals
