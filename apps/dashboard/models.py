from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class UserActivity(TimeStampedModel):
    """Kullanıcı aktivite takibi"""
    ACTIVITY_TYPES = (
        ('login', 'Giriş'),
        ('logout', 'Çıkış'),
        ('profile_update', 'Profil Güncellendi'),
        ('job_view', 'İlan Görüntülendi'),
        ('job_apply', 'İş Başvurusu'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()}"
    
    class Meta:
        ordering = ['-created_at']


class Notification(TimeStampedModel):
    """Kullanıcı bildirimleri"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']
      
