# apps/posts/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from apps.core.models import TimeStampedModel
from django.core.validators import FileExtensionValidator
import uuid


class PostCategory(TimeStampedModel):
    """Post kategorileri"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Kategori Adı')
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, verbose_name='Açıklama')
    icon = models.CharField(max_length=50, blank=True, verbose_name='İkon')
    color = models.CharField(max_length=7, default='#0a66c2', verbose_name='Renk')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    
    class Meta:
        verbose_name = 'Post Kategorisi'
        verbose_name_plural = 'Post Kategorileri'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Post(TimeStampedModel):
    """Ana post modeli"""
    POST_TYPES = (
        ('text', 'Metin'),
        ('image', 'Fotoğraf'),
        ('video', 'Video'),
        ('link', 'Link'),
        ('poll', 'Anket'),
        ('event', 'Etkinlik'),
        ('job', 'İş İlanı'),
    )
    
    VISIBILITY_CHOICES = (
        ('public', 'Herkese Açık'),
        ('followers', 'Takipçiler'),
        ('private', 'Sadece Ben'),
    )
    
    # Basic Info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='text')
    
    # Content
    content = models.TextField(verbose_name='İçerik')
    title = models.CharField(max_length=200, blank=True, verbose_name='Başlık')
    
    # Media
    image = models.ImageField(
        upload_to='posts/images/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp'])],
        verbose_name='Fotoğraf'
    )
    video = models.FileField(
        upload_to='posts/videos/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['mp4', 'avi', 'mov', 'webm'])],
        verbose_name='Video'
    )
    
    # Link sharing
    link_url = models.URLField(blank=True, verbose_name='Link URL')
    link_title = models.CharField(max_length=200, blank=True, verbose_name='Link Başlık')
    link_description = models.TextField(blank=True, verbose_name='Link Açıklama')
    link_image = models.URLField(blank=True, verbose_name='Link Görsel')
    
    # Organization
    category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True, verbose_name='Etiketler')
    location = models.CharField(max_length=100, blank=True, verbose_name='Konum')
    
    # Settings
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    allow_comments = models.BooleanField(default=True, verbose_name='Yorumlara İzin Ver')
    is_pinned = models.BooleanField(default=False, verbose_name='Sabitlenmiş')
    is_featured = models.BooleanField(default=False, verbose_name='Öne Çıkan')
    
    # Moderation
    is_published = models.BooleanField(default=True, verbose_name='Yayınlanmış')
    is_approved = models.BooleanField(default=True, verbose_name='Onaylanmış')
    is_deleted = models.BooleanField(default=False, verbose_name='Silinmiş')
    
    # Statistics (will be updated by signals)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Gönderi'
        verbose_name_plural = 'Gönderiler'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['post_type', '-created_at']),
            models.Index(fields=['is_published', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.get_full_name()} - {self.content[:50]}"
    
    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'pk': self.pk})
    
    def get_tags_list(self):
        """Etiketleri liste olarak döndür"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def is_liked_by(self, user):
        """Kullanıcı bu postu beğenmiş mi?"""
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False
    
    def is_saved_by(self, user):
        """Kullanıcı bu postu kaydetmiş mi?"""
        if user.is_authenticated:
            return self.saved_posts.filter(user=user).exists()
        return False


class PostLike(TimeStampedModel):
    """Post beğenileri"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Beğeni'
        verbose_name_plural = 'Beğeniler'
        unique_together = ('post', 'user')
        indexes = [
            models.Index(fields=['post', 'user']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} -> {self.post.content[:30]}"


class PostComment(TimeStampedModel):
    """Post yorumları"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField(verbose_name='Yorum')
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # Statistics
    likes_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Yorum'
        verbose_name_plural = 'Yorumlar'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f"{self.author.get_full_name()} -> {self.content[:30]}"
    
    def get_replies(self):
        """Alt yorumları getir"""
        return self.replies.filter(is_deleted=False).order_by('created_at')


class PostCommentLike(TimeStampedModel):
    """Yorum beğenileri"""
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Yorum Beğenisi'
        verbose_name_plural = 'Yorum Beğenileri'
        unique_together = ('comment', 'user')
    
    def __str__(self):
        return f"{self.user.get_full_name()} -> {self.comment.content[:30]}"


class PostSave(TimeStampedModel):
    """Kaydedilen postlar"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_posts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Kayıtlı Gönderi'
        verbose_name_plural = 'Kayıtlı Gönderiler'
        unique_together = ('post', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} -> {self.post.content[:30]}"


class PostShare(TimeStampedModel):
    """Post paylaşımları"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shared_to = models.CharField(
        max_length=50,
        choices=[
            ('timeline', 'Zaman Tüneli'),
            ('message', 'Mesaj'),
            ('external', 'Dış Platform'),
        ],
        default='timeline'
    )
    note = models.TextField(blank=True, verbose_name='Not')
    
    class Meta:
        verbose_name = 'Paylaşım'
        verbose_name_plural = 'Paylaşımlar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} -> {self.post.content[:30]}"


class PostView(TimeStampedModel):
    """Post görüntülenmeleri"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Görüntülenme'
        verbose_name_plural = 'Görüntülenmeler'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.post.content[:30]} - {self.ip_address}"


class Poll(TimeStampedModel):
    """Anket sistemi"""
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='poll')
    question = models.CharField(max_length=300, verbose_name='Soru')
    multiple_choice = models.BooleanField(default=False, verbose_name='Çoklu Seçim')
    allow_add_option = models.BooleanField(default=False, verbose_name='Seçenek Eklemeye İzin Ver')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Bitiş Tarihi')
    
    # Statistics
    total_votes = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Anket'
        verbose_name_plural = 'Anketler'
    
    def __str__(self):
        return self.question
    
    def is_expired(self):
        """Anket süresi dolmuş mu?"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    def can_vote(self, user):
        """Kullanıcı oy verebilir mi?"""
        if not user.is_authenticated or self.is_expired():
            return False
        return not self.votes.filter(user=user).exists()


class PollOption(TimeStampedModel):
    """Anket seçenekleri"""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200, verbose_name='Seçenek Metni')
    votes_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Anket Seçeneği'
        verbose_name_plural = 'Anket Seçenekleri'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.poll.question} - {self.text}"
    
    def get_percentage(self):
        """Oy yüzdesini hesapla"""
        if self.poll.total_votes > 0:
            return round((self.votes_count / self.poll.total_votes) * 100, 1)
        return 0


class PollVote(TimeStampedModel):
    """Anket oyları"""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Anket Oyu'
        verbose_name_plural = 'Anket Oyları'
        unique_together = ('poll', 'user', 'option')
    
    def __str__(self):
        return f"{self.user.get_full_name()} -> {self.option.text}"


class Event(TimeStampedModel):
    """Etkinlik sistemi"""
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='event')
    title = models.CharField(max_length=200, verbose_name='Etkinlik Adı')
    description = models.TextField(verbose_name='Açıklama')
    
    # Date & Time
    start_date = models.DateTimeField(verbose_name='Başlangıç Tarihi')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Bitiş Tarihi')
    timezone = models.CharField(max_length=50, default='Europe/Istanbul', verbose_name='Saat Dilimi')
    
    # Location
    location_name = models.CharField(max_length=200, blank=True, verbose_name='Mekan Adı')
    address = models.TextField(blank=True, verbose_name='Adres')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Settings
    is_online = models.BooleanField(default=False, verbose_name='Online Etkinlik')
    online_url = models.URLField(blank=True, verbose_name='Online Link')
    max_participants = models.PositiveIntegerField(null=True, blank=True, verbose_name='Maksimum Katılımcı')
    registration_required = models.BooleanField(default=False, verbose_name='Kayıt Gerekli')
    is_free = models.BooleanField(default=True, verbose_name='Ücretsiz')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Fiyat')
    
    # Statistics
    participants_count = models.PositiveIntegerField(default=0)
    interested_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Etkinlik'
        verbose_name_plural = 'Etkinlikler'
        ordering = ['start_date']
    
    def __str__(self):
        return self.title
    
    def is_past(self):
        """Etkinlik geçmiş mi?"""
        from django.utils import timezone
        return timezone.now() > self.start_date
    
    def is_full(self):
        """Etkinlik dolu mu?"""
        if self.max_participants:
            return self.participants_count >= self.max_participants
        return False


class EventParticipant(TimeStampedModel):
    """Etkinlik katılımcıları"""
    STATUS_CHOICES = (
        ('going', 'Katılacak'),
        ('maybe', 'Belki'),
        ('interested', 'İlgili'),
        ('not_going', 'Katılmayacak'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='going')
    
    class Meta:
        verbose_name = 'Etkinlik Katılımcısı'
        verbose_name_plural = 'Etkinlik Katılımcıları'
        unique_together = ('event', 'user')
    
    def __str__(self):
        return f"{self.user.get_full_name()} -> {self.event.title} ({self.status})"
      
