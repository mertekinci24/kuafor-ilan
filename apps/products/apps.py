from django.apps import AppConfig

class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = 'E-Commerce Sistemi'
    
    def ready(self):
        # Signals'ları import et (eğer varsa)
        try:
            import apps.products.signals
        except ImportError:
            pass