from django.db import models
from django.conf import settings
# from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid

# User = get_user_model()


class NotificationType(models.Model):
    """Bildirim türleri"""
    NOTIFICATION_TYPES = [
        # İş İlanı Bildirimleri
        ('job_application', 'İş Başvurusu'),
        ('job_application_status', 'Başvuru Durumu Değişikliği'),
        ('new_job_match', 'Uygun İş İlanı'),
        ('job_deadline', 'İlan Son Başvuru Tarihi'),
        
        # Mesaj Bildirimleri
        ('new_message', 'Yeni Mesaj'),
        ('message_read', 'Mesaj Okundu'),
        
        # Sosyal Bildirimleri
        ('post_like', 'Gönderi Beğenisi'),
        ('post_comment', 'Gönderi Yorumu'),
        ('post_share', 'Gönderi Paylaşımı'),
        ('new_follower', 'Yeni Takipçi'),
        
        # Sistem Bildirimleri
        ('system_update', 'Sistem Güncellemesi'),
        ('account_security', 'Hesap Güvenliği'),
        ('profile_incomplete', 'Profil Eksiklikleri'),
        ('verification_status', 'Doğrulama Durumu'),
        
        # İş Veren Bildirimleri
        ('new_application', 'Yeni Başvuru'),
        ('application_deadline', 'Başvuru Süresi Bitiyor'),
        ('profile_view', 'Profil Görüntülendi'),
        
        # Özel Bildirimler
        ('promotion', 'Promosyon'),
        ('newsletter', 'Haber Bülteni'),
        ('event_reminder', 'Etkinlik Hatırlatması'),
    ]
    
    code = models.CharField(max_length=50, unique=True, choices=NOTIFICATION_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-bell')
    color = models.CharField(max_length=7, default='#007bff')
    is_active = models.BooleanField(default=True)
    
    # Email ve SMS ayarları
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bildirim Türü'
        verbose_name_plural = 'Bildirim Türleri'
        ordering = ['name']

    def __str__(self):
        return self.name


class Notification(models.Model):
    """Ana bildirim modeli"""
    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('normal', 'Normal'),
        ('high', 'Yüksek'),
        ('urgent', 'Acil'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    
    # Bildirim içeriği
    title = models.CharField(max_length=200)
    message = models.TextField()
    short_message = models.CharField(max_length=100, blank=True)  # Kısa özet
    
    # İlgili nesne (Generic Foreign Key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Bildirim ayarları
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    action_url = models.URLField(blank=True, null=True)  # Tıklandığında gidilecek URL
    action_text = models.CharField(max_length=50, blank=True)  # Buton metni
    
    # Durum bilgileri
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Email/SMS durumu
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    sms_sent = models.BooleanField(default=False)
    sms_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Zaman bilgileri
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Bildirim süre sonu

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bildirim'
        verbose_name_plural = 'Bildirimler'
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['notification_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.recipient.get_full_name()}: {self.title}"

    def mark_as_read(self):
        """Bildirimi okundu olarak işaretle"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def mark_as_sent(self):
        """Bildirimi gönderildi olarak işaretle"""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(update_fields=['is_sent', 'sent_at'])

    def mark_as_delivered(self):
        """Bildirimi teslim edildi olarak işaretle"""
        if not self.is_delivered:
            self.is_delivered = True
            self.delivered_at = timezone.now()
            self.save(update_fields=['is_delivered', 'delivered_at'])

    def is_expired(self):
        """Bildirim süresi dolmuş mu?"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def get_icon(self):
        """Bildirim ikonu"""
        return self.notification_type.icon

    def get_color(self):
        """Bildirim rengi"""
        return self.notification_type.color

    def get_priority_class(self):
        """Öncelik CSS sınıfı"""
        priority_classes = {
            'low': 'text-muted',
            'normal': 'text-primary',
            'high': 'text-warning',
            'urgent': 'text-danger',
        }
        return priority_classes.get(self.priority, 'text-primary')

    @classmethod
    def create_notification(cls, recipient, notification_type_code, title, message, **kwargs):
        """Yeni bildirim oluştur"""
        try:
            notification_type = NotificationType.objects.get(code=notification_type_code, is_active=True)
            
            notification = cls.objects.create(
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
            
            # E-posta ve SMS gönderim işlemleri buraya eklenebilir
            # notification.send_email() gibi
            
            return notification
            
        except NotificationType.DoesNotExist:
            # Log error
            return None


class UserNotificationSettings(models.Model):
    """Kullanıcı bildirim ayarları"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Genel ayarlar
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    # İş bildirimleri
    job_applications = models.BooleanField(default=True)
    job_matches = models.BooleanField(default=True)
    job_deadlines = models.BooleanField(default=True)
    
    # Mesaj bildirimleri
    new_messages = models.BooleanField(default=True)
    message_read_receipts = models.BooleanField(default=False)
    
    # Sosyal bildirimler
    post_interactions = models.BooleanField(default=True)
    new_followers = models.BooleanField(default=True)
    
    # Sistem bildirimleri
    system_updates = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    
    # Pazarlama bildirimleri
    promotions = models.BooleanField(default=False)
    newsletters = models.BooleanField(default=False)
    
    # Sessiz saatler
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='08:00')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Kullanıcı Bildirim Ayarları'
        verbose_name_plural = 'Kullanıcı Bildirim Ayarları'

    def __str__(self):
        return f"{self.user.get_full_name()} - Bildirim Ayarları"

    def is_notification_allowed(self, notification_type_code):
        """Bu bildirim türü için izin var mı?"""
        type_mapping = {
            'job_application': self.job_applications,
            'job_application_status': self.job_applications,
            'new_job_match': self.job_matches,
            'job_deadline': self.job_deadlines,
            'new_message': self.new_messages,
            'message_read': self.message_read_receipts,
            'post_like': self.post_interactions,
            'post_comment': self.post_interactions,
            'post_share': self.post_interactions,
            'new_follower': self.new_followers,
            'system_update': self.system_updates,
            'account_security': self.security_alerts,
            'promotion': self.promotions,
            'newsletter': self.newsletters,
        }
        return type_mapping.get(notification_type_code, True)

    def is_quiet_hours(self):
        """Şu anda sessiz saatler mi?"""
        if not self.quiet_hours_enabled:
            return False
        
        now = timezone.now().time()
        if self.quiet_hours_start <= self.quiet_hours_end:
            return self.quiet_hours_start <= now <= self.quiet_hours_end
        else:  # Gecenin üzerinden geçen durum
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end


class NotificationTemplate(models.Model):
    """Bildirim şablonları"""
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=100)
    
    # Şablon içerikleri
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    email_subject_template = models.CharField(max_length=200, blank=True)
    email_body_template = models.TextField(blank=True)
    sms_template = models.CharField(max_length=160, blank=True)
    
    # Şablon değişkenleri (JSON formatında)
    variables = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bildirim Şablonu'
        verbose_name_plural = 'Bildirim Şablonları'

    def __str__(self):
        return f"{self.notification_type.name} - {self.name}"

    def render(self, context):
        """Şablonu render et"""
        title = self.title_template.format(**context)
        message = self.message_template.format(**context)
        return title, message


class NotificationBatch(models.Model):
    """Toplu bildirim gönderimi"""
    name = models.CharField(max_length=100)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    
    # Hedef kitle
    recipient_filter = models.JSONField(default=dict)  # Filtreleme kriterleri
    total_recipients = models.PositiveIntegerField(default=0)
    
    # İçerik
    title = models.CharField(max_length=200)
    message = models.TextField()
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=50, blank=True)
    
    # Durum
    is_sent = models.BooleanField(default=False)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    
    # Zamanlama
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_notification_batches')

    class Meta:
        verbose_name = 'Toplu Bildirim'
        verbose_name_plural = 'Toplu Bildirimler'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.total_recipients} alıcı"
      
