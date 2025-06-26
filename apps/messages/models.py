from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class Conversation(models.Model):
    """İki kullanıcı arasındaki sohbet"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Son mesaj bilgileri (cache için)
    last_message = models.TextField(blank=True, null=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_message_sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='last_messages_sent'
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Sohbet'
        verbose_name_plural = 'Sohbetler'

    def __str__(self):
        participants_names = ', '.join([p.get_full_name() or p.email for p in self.participants.all()[:2]])
        return f"Sohbet: {participants_names}"

    def get_other_participant(self, user):
        """Karşı tarafı getir"""
        return self.participants.exclude(id=user.id).first()

    def get_participant_names(self):
        """Katılımcı isimlerini getir"""
        return [p.get_full_name() or p.email for p in self.participants.all()]

    def mark_as_read(self, user):
        """Kullanıcı için okundu işaretle"""
        self.messages.filter(sender__ne=user, is_read=False).update(is_read=True, read_at=timezone.now())

    def get_unread_count(self, user):
        """Okunmamış mesaj sayısı"""
        return self.messages.filter(sender__ne=user, is_read=False).count()

    def update_last_message(self, message):
        """Son mesaj bilgilerini güncelle"""
        self.last_message = message.content[:100]
        self.last_message_at = message.created_at
        self.last_message_sender = message.sender
        self.updated_at = timezone.now()
        self.save(update_fields=['last_message', 'last_message_at', 'last_message_sender', 'updated_at'])


class Message(models.Model):
    """Mesaj modeli"""
    MESSAGE_TYPES = [
        ('text', 'Metin'),
        ('image', 'Resim'),
        ('file', 'Dosya'),
        ('job_share', 'İş İlanı Paylaşımı'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    # Medya dosyaları
    image = models.ImageField(upload_to='messages/images/', blank=True, null=True)
    file = models.FileField(upload_to='messages/files/', blank=True, null=True)
    
    # İş ilanı paylaşımı için
    shared_job = models.ForeignKey(
        'jobs.JobListing', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='shared_in_messages'
    )
    
    # Mesaj durumu
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Zaman bilgileri
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Mesaj'
        verbose_name_plural = 'Mesajlar'

    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.sender.get_full_name()}: {content_preview}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Yeni mesajsa sohbeti güncelle
        if is_new:
            self.conversation.update_last_message(self)

    def mark_as_read(self):
        """Mesajı okundu olarak işaretle"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def get_file_name(self):
        """Dosya adını getir"""
        if self.file:
            return self.file.name.split('/')[-1]
        return None

    def get_file_size(self):
        """Dosya boyutunu getir"""
        if self.file:
            return self.file.size
        return None

    def can_edit(self, user):
        """Kullanıcı bu mesajı düzenleyebilir mi?"""
        return self.sender == user and not self.is_deleted

    def can_delete(self, user):
        """Kullanıcı bu mesajı silebilir mi?"""
        return self.sender == user and not self.is_deleted


class MessageAttachment(models.Model):
    """Mesaj eki modeli"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='messages/attachments/')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mesaj Eki'
        verbose_name_plural = 'Mesaj Ekleri'

    def __str__(self):
        return f"{self.message} - {self.file_name}"

    @property
    def is_image(self):
        """Dosya resim mi?"""
        return self.file_type.startswith('image/')

    @property
    def is_document(self):
        """Dosya döküman mı?"""
        document_types = ['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx']
        return any(self.file_type.endswith(ext) for ext in document_types)


class BlockedUser(models.Model):
    """Engellenen kullanıcılar"""
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    blocked_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['blocker', 'blocked']
        verbose_name = 'Engellenen Kullanıcı'
        verbose_name_plural = 'Engellenen Kullanıcılar'

    def __str__(self):
        return f"{self.blocker.get_full_name()} → {self.blocked.get_full_name()}"


class MessageReport(models.Model):
    """Mesaj şikayetleri"""
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Taciz'),
        ('inappropriate', 'Uygunsuz İçerik'),
        ('fake_job', 'Sahte İş İlanı'),
        ('other', 'Diğer'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['message', 'reporter']
        verbose_name = 'Mesaj Şikayeti'
        verbose_name_plural = 'Mesaj Şikayetleri'

    def __str__(self):
        return f"Şikayet: {self.message} - {self.get_reason_display()}"
      
