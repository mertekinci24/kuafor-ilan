from django.contrib.auth import get_user_model
from .models import Notification, NotificationType, UserNotificationSettings
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """Bildirim servisi - bildirim gönderme ve yönetim işlemleri"""
    
    @staticmethod
    def create_notification(recipient, notification_type_code, title, message, **kwargs):
        """Yeni bildirim oluştur"""
        try:
            # Kullanıcının bildirim ayarlarını kontrol et
            settings, created = UserNotificationSettings.objects.get_or_create(user=recipient)
            
            if not settings.is_notification_allowed(notification_type_code):
                logger.info(f"Notification blocked by user settings: {notification_type_code} for {recipient.email}")
                return None
            
            # Sessiz saatleri kontrol et
            if settings.is_quiet_hours():
                logger.info(f"Notification postponed due to quiet hours: {notification_type_code} for {recipient.email}")
                # Gelecekte: Sessiz saatler sonrası için zamanla
                return None
            
            # Bildirim türünü bul
            try:
                notification_type = NotificationType.objects.get(code=notification_type_code, is_active=True)
            except NotificationType.DoesNotExist:
                logger.error(f"Notification type not found: {notification_type_code}")
                return None
            
            # Bildirimi oluştur
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                short_message=kwargs.get('short_message', message[:100]),
                priority=kwargs.get('priority', 'normal'),
                action_url=kwargs.get('action_url'),
                action_text=kwargs.get('action_text'),
                content_object=kwargs.get('content_object'),
                expires_at=kwargs.get('expires_at'),
            )
            
            # Email/SMS gönderim kontrolü
            if notification_type.send_email and settings.email_notifications:
                NotificationService._send_email(notification)
            
            if notification_type.send_sms and settings.sms_notifications:
                NotificationService._send_sms(notification)
            
            logger.info(f"Notification created: {notification.id} for {recipient.email}")
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            return None
    
    @staticmethod
    def _send_email(notification):
        """Email gönderimi"""
        try:
            # Django email backend kullanarak email gönder
            from django.core.mail import send_mail
            from django.conf import settings as django_settings
            
            subject = notification.title
            message = notification.message
            from_email = getattr(django_settings, 'DEFAULT_FROM_EMAIL', 'noreply@kuaforlian.com')
            recipient_list = [notification.recipient.email]
            
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            
            notification.email_sent = True
            notification.email_sent_at = timezone.now()
            notification.save(update_fields=['email_sent', 'email_sent_at'])
            
            logger.info(f"Email sent for notification: {notification.id}")
            
        except Exception as e:
            logger.error(f"Error sending email for notification {notification.id}: {str(e)}")
    
    @staticmethod
    def _send_sms(notification):
        """SMS gönderimi"""
        try:
            # SMS servisi entegrasyonu buraya eklenecek
            # Örnek: Twilio, Vonage, vs.
            
            # Şimdilik sadece log
            logger.info(f"SMS would be sent for notification: {notification.id}")
            
            notification.sms_sent = True
            notification.sms_sent_at = timezone.now()
            notification.save(update_fields=['sms_sent', 'sms_sent_at'])
            
        except Exception as e:
            logger.error(f"Error sending SMS for notification {notification.id}: {str(e)}")
    
    @staticmethod
    def mark_all_as_read(user):
        """Kullanıcının tüm bildirimlerini okundu olarak işaretle"""
        from django.utils import timezone
        
        updated_count = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        logger.info(f"Marked {updated_count} notifications as read for user {user.email}")
        return updated_count
    
    @staticmethod
    def get_unread_count(user):
        """Kullanıcının okunmamış bildirim sayısı"""
        return Notification.objects.filter(
            recipient=user,
            is_read=False
        ).count()
    
    @staticmethod
    def clean_old_notifications(days=30):
        """Eski bildirimleri temizle"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()[0]
        
        logger.info(f"Cleaned {deleted_count} old notifications")
        return deleted_count
    
    @staticmethod
    def create_system_notification(title, message, priority='normal'):
        """Tüm kullanıcılara sistem bildirimi gönder"""
        users = User.objects.filter(is_active=True)
        created_count = 0
        
        for user in users:
            notification = NotificationService.create_notification(
                recipient=user,
                notification_type_code='system_update',
                title=title,
                message=message,
                priority=priority
            )
            if notification:
                created_count += 1
        
        logger.info(f"System notification sent to {created_count} users")
        return created_count
      
