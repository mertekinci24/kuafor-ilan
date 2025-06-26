from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.messages'
    verbose_name = 'Mesajlaşma'
    
    def ready(self):
        """App hazır olduğunda çalışacak kod"""
        import apps.messages.signals
      
