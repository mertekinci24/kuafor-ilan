from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Bildirimler'
    
    def ready(self):
        """App hazır olduğunda çalışacak kod"""
        import apps.notifications.signals
      
