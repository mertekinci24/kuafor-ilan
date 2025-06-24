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
    
    # Statistics
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Gönderi'
        verbose_name_plural = 'Gönderiler'
        ordering = ['-created_at']
    
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
    
    def __str__(self):
        return f"{self.author.get_full_name()} -> {self.content[:30]}"


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
        
