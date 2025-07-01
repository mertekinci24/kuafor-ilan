from django.apps import AppConfig

class MembershipsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.memberships'
    verbose_name = 'Üyelik Sistemi'
    
    def ready(self):
        # Signals'ları import et (eğer varsa)
        try:
            import apps.memberships.signals
        except ImportError:
            pass