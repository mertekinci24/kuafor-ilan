from django.contrib import admin
from django.utils.html import format_html
from .models import PostCategory, Post, PostLike, PostComment, PostSave

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
    
