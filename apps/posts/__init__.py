# 1. apps/posts/__init__.py
# (Boş dosya)

# 2. apps/posts/apps.py
from django.apps import AppConfig

class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.posts'
    verbose_name = 'Gönderiler'
    
    def ready(self):
        import apps.posts.signals

# 3. apps/posts/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PostCategory, Post, PostLike, PostComment, PostCommentLike,
    PostSave, PostShare, PostView, Poll, PollOption, PollVote,
    Event, EventParticipant
)

@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; width: 20px; height: 20px; display: inline-block; border-radius: 3px;"></span>',
            obj.color
        )
    color_display.short_description = 'Renk'

class PostLikeInline(admin.TabularInline):
    model = PostLike
    extra = 0
    readonly_fields = ['user', 'created_at']

class PostCommentInline(admin.TabularInline):
    model = PostComment
    extra = 0
    readonly_fields = ['author', 'created_at']
    fields = ['author', 'content', 'parent', 'is_deleted', 'created_at']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'author', 'post_type', 'content_preview', 'category',
        'likes_count', 'comments_count', 'is_published', 'created_at'
    ]
    list_filter = [
        'post_type', 'category', 'is_published', 'is_approved',
        'is_featured', 'is_pinned', 'created_at'
    ]
    search_fields = ['content', 'title', 'author__first_name', 'author__last_name', 'author__email']
    readonly_fields = [
        'id', 'likes_count', 'comments_count', 'shares_count', 
        'views_count', 'created_at', 'updated_at'
    ]
    inlines = [PostLikeInline, PostCommentInline]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('id', 'author', 'post_type', 'title', 'content')
        }),
        ('Medya', {
            'fields': ('image', 'video', 'link_url', 'link_title', 'link_description'),
            'classes': ('collapse',)
        }),
        ('Organizasyon', {
            'fields': ('category', 'tags', 'location', 'visibility')
        }),
        ('Ayarlar', {
            'fields': ('allow_comments', 'is_pinned', 'is_featured')
        }),
        ('Moderasyon', {
            'fields': ('is_published', 'is_approved', 'is_deleted')
        }),
        ('İstatistikler', {
            'fields': ('likes_count', 'comments_count', 'shares_count', 'views_count'),
            'classes': ('collapse',)
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'İçerik Önizleme'

@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'author', 'content_preview', 'parent', 'likes_count', 'created_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['content', 'author__first_name', 'author__email']
    readonly_fields = ['likes_count', 'replies_count']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Yorum'

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__email', 'post__content']

@admin.register(PostSave)
class PostSaveAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__email']

class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 2
    readonly_fields = ['votes_count']

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['question', 'post', 'total_votes', 'expires_at', 'created_at']
    list_filter = ['multiple_choice', 'expires_at', 'created_at']
    search_fields = ['question', 'post__content']
    inlines = [PollOptionInline]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'post', 'start_date', 'location_name', 
        'participants_count', 'is_online', 'is_free'
    ]
    list_filter = ['is_online', 'is_free', 'registration_required', 'start_date']
    search_fields = ['title', 'description', 'location_name']
    readonly_fields = ['participants_count', 'interested_count']

# 4. apps/posts/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PostLike, PostComment, PostShare, PostView, PollVote, EventParticipant

@receiver(post_save, sender=PostLike)
@receiver(post_delete, sender=PostLike)
def update_post_likes_count(sender, instance, **kwargs):
    """Post beğeni sayısını güncelle"""
    post = instance.post
    post.likes_count = post.likes.count()
    post.save(update_fields=['likes_count'])

@receiver(post_save, sender=PostComment)
@receiver(post_delete, sender=PostComment)
def update_post_comments_count(sender, instance, **kwargs):
    """Post yorum sayısını güncelle"""
    if not instance.is_deleted:
        post = instance.post
        post.comments_count = post.comments.filter(is_deleted=False).count()
        post.save(update_fields=['comments_count'])

@receiver(post_save, sender=PostShare)
@receiver(post_delete, sender=PostShare)
def update_post_shares_count(sender, instance, **kwargs):
    """Post paylaşım sayısını güncelle"""
    post = instance.post
    post.shares_count = post.shares.count()
    post.save(update_fields=['shares_count'])

@receiver(post_save, sender=PostView)
def update_post_views_count(sender, instance, created, **kwargs):
    """Post görüntülenme sayısını güncelle"""
    if created:
        post = instance.post
        post.views_count = post.post_views.count()
        post.save(update_fields=['views_count'])

@receiver(post_save, sender=PollVote)
@receiver(post_delete, sender=PollVote)
def update_poll_votes_count(sender, instance, **kwargs):
    """Anket oy sayılarını güncelle"""
    poll = instance.poll
    option = instance.option
    
    # Option vote count
    option.votes_count = option.votes.count()
    option.save(update_fields=['votes_count'])
    
    # Total poll votes
    poll.total_votes = poll.votes.count()
    poll.save(update_fields=['total_votes'])

@receiver(post_save, sender=EventParticipant)
@receiver(post_delete, sender=EventParticipant)
def update_event_participants_count(sender, instance, **kwargs):
    """Etkinlik katılımcı sayılarını güncelle"""
    event = instance.event
    
    # Going participants
    event.participants_count = event.participants.filter(status='going').count()
    
    # Interested participants
    event.interested_count = event.participants.filter(status='interested').count()
    
    event.save(update_fields=['participants_count', 'interested_count'])

# 5. apps/posts/urls.py
from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Post CRUD
    path('', views.posts_list_view, name='list'),
    path('create/', views.post_create_view, name='create'),
    path('<uuid:pk>/', views.post_detail_view, name='detail'),
    path('<uuid:pk>/edit/', views.post_edit_view, name='edit'),
    path('<uuid:pk>/delete/', views.post_delete_view, name='delete'),
    
    # Post Actions API
    path('api/like/', views.post_like_api, name='like_api'),
    path('api/save/', views.post_save_api, name='save_api'),
    path('api/share/', views.post_share_api, name='share_api'),
    path('api/view/', views.post_view_api, name='view_api'),
    
    # Comments API
    path('api/comments/', views.comments_api, name='comments_api'),
    path('api/comments/create/', views.comment_create_api, name='comment_create_api'),
    path('api/comments/<int:comment_id>/like/', views.comment_like_api, name='comment_like_api'),
    path('api/comments/<int:comment_id>/delete/', views.comment_delete_api, name='comment_delete_api'),
    
    # Poll API
    path('api/poll/vote/', views.poll_vote_api, name='poll_vote_api'),
    
    # Event API
    path('api/event/participate/', views.event_participate_api, name='event_participate_api'),
    
    # Feed API
    path('api/feed/', views.feed_api, name='feed_api'),
    path('api/trending/', views.trending_api, name='trending_api'),
]

# 6. Settings güncellemesi için: kuafor_ilan/settings.py'ye eklenecek
"""
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.core',
    'apps.authentication',
    'apps.dashboard',
    'apps.jobs',
    'apps.profiles',
    'apps.posts',  # BU SATIRI EKLEYİN
]
"""

# 7. Main URLs güncellemesi için: kuafor_ilan/urls.py'ye eklenecek
"""
urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Ana sayfa
    path('', home_view, name='home'),
    
    # Authentication URL'leri
    path('auth/', include('apps.authentication.urls')),
    
    # Dashboard URL'leri
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Jobs URL'leri
    path('jobs/', include('apps.jobs.urls')),
    
    # Profiles URL'leri
    path('profiles/', include('apps.profiles.urls')),
    
    # Posts URL'leri - BU SATIRI EKLEYİN
    path('posts/', include('apps.posts.urls')),
    
    # WordPress bot koruması
    # ... rest of URLs
]
"""
