from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.messages'
    verbose_name = 'Mesajlaşma'
    label = 'messaging'  # Çakışmayı önlemek için özel etiket
    
