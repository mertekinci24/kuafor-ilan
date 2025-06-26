# Bildirim signal'ları buraya eklenecek
# Şimdilik boş bırakıyoruz

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification, UserNotificationSettings

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_notification_settings(sender, instance, created, **kwargs):
    """Yeni kullanıcı oluşturulduğunda bildirim ayarları oluştur"""
    if created:
        UserNotificationSettings.objects.create(
            user=instance,
            email_notifications=True,
            push_notifications=True,
            job_applications=True,
            job_matches=True,
            new_messages=True,
            post_interactions=True,
            system_updates=True,
        )


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    """Yeni bildirim oluşturulduğunda gönderim işlemleri"""
    if created and not instance.is_sent:
        # Email/SMS/Push gönderim işlemleri buraya eklenecek
        instance.mark_as_sent()


# Gelecekte eklenebilecek signal'lar:
# - Email gönderimi
# - SMS gönderimi  
# - Push notification gönderimi
# - Real-time bildirimler
