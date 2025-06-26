from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Conversation, Message, MessageAttachment, BlockedUser, MessageReport


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_participants', 'last_message_preview', 'last_message_at', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['participants__email', 'participants__first_name', 'participants__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['participants']
    date_hierarchy = 'created_at'
    
    def get_participants(self, obj):
        """Katılımcıları göster"""
        participants = obj.participants.all()[:2]
        names = [p.get_full_name() or p.email for p in participants]
        return ' ↔ '.join(names)
    get_participants.short_description = 'Katılımcılar'
    
    def last_message_preview(self, obj):
        """Son mesaj önizlemesi"""
        if obj.last_message:
            preview = obj.last_message[:50] + '...' if len(obj.last_message) > 50 else obj.last_message
            return format_html('<span title="{}">{}</span>', obj.last_message, preview)
        return '-'
    last_message_preview.short_description = 'Son Mesaj'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('participants')


class MessageAttachmentInline(admin.TabularInline):
    model = MessageAttachment
    extra = 0
    readonly_fields = ['file_size', 'file_type', 'uploaded_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender_info', 'conversation_info', 'content_preview', 'message_type', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'is_deleted', 'created_at']
    search_fields = ['content', 'sender__email', 'sender__first_name', 'sender__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'read_at', 'deleted_at']
    raw_id_fields = ['conversation', 'sender', 'shared_job']
    date_hierarchy = 'created_at'
    inlines = [MessageAttachmentInline]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('id', 'conversation', 'sender', 'message_type', 'content')
        }),
        ('Medya', {
            'fields': ('image', 'file', 'shared_job'),
            'classes': ('collapse',)
        }),
        ('Durum', {
            'fields': ('is_read', 'read_at', 'is_deleted', 'deleted_at')
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def sender_info(self, obj):
        """Gönderen bilgisi"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:authentication_customuser_change', args=[obj.sender.pk]),
            obj.sender.get_full_name() or obj.sender.email
        )
    sender_info.short_description = 'Gönderen'
    
    def conversation_info(self, obj):
        """Sohbet bilgisi"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:messages_conversation_change', args=[obj.conversation.pk]),
            str(obj.conversation)[:50]
        )
    conversation_info.short_description = 'Sohbet'
    
    def content_preview(self, obj):
        """İçerik önizlemesi"""
        if obj.content:
            preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
            return format_html('<span title="{}">{}</span>', obj.content, preview)
        return '-'
    content_preview.short_description = 'İçerik'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'conversation')
    
    actions = ['mark_as_read', 'mark_as_deleted']
    
    def mark_as_read(self, request, queryset):
        """Seçili mesajları okundu olarak işaretle"""
        updated = queryset.filter(is_read=False).update(
            is_read=True, 
            read_at=timezone.now()
        )
        self.message_user(request, f'{updated} mesaj okundu olarak işaretlendi.')
    mark_as_read.short_description = 'Seçili mesajları okundu olarak işaretle'
    
    def mark_as_deleted(self, request, queryset):
        """Seçili mesajları sil"""
        updated = queryset.filter(is_deleted=False).update(
            is_deleted=True, 
            deleted_at=timezone.now()
        )
        self.message_user(request, f'{updated} mesaj silindi.')
    mark_as_deleted.short_description = 'Seçili mesajları sil'


@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'message_info', 'file_name', 'file_type', 'file_size_display', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['file_name', 'message__content', 'message__sender__email']
    readonly_fields = ['file_size', 'file_type', 'uploaded_at']
    raw_id_fields = ['message']
    date_hierarchy = 'uploaded_at'
    
    def message_info(self, obj):
        """Mesaj bilgisi"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:messages_message_change', args=[obj.message.pk]),
            str(obj.message)[:50]
        )
    message_info.short_description = 'Mesaj'
    
    def file_size_display(self, obj):
        """Dosya boyutu"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f'{obj.file_size} B'
            elif obj.file_size < 1024 * 1024:
                return f'{obj.file_size / 1024:.1f} KB'
            else:
                return f'{obj.file_size / (1024 * 1024):.1f} MB'
        return '-'
    file_size_display.short_description = 'Dosya Boyutu'


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ['blocker_info', 'blocked_info', 'reason', 'blocked_at']
    list_filter = ['blocked_at']
    search_fields = ['blocker__email', 'blocked__email', 'reason']
    readonly_fields = ['blocked_at']
    raw_id_fields = ['blocker', 'blocked']
    date_hierarchy = 'blocked_at'
    
    def blocker_info(self, obj):
        """Engelleyen kullanıcı"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:authentication_customuser_change', args=[obj.blocker.pk]),
            obj.blocker.get_full_name() or obj.blocker.email
        )
    blocker_info.short_description = 'Engelleyen'
    
    def blocked_info(self, obj):
        """Engellenen kullanıcı"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:authentication_customuser_change', args=[obj.blocked.pk]),
            obj.blocked.get_full_name() or obj.blocked.email
        )
    blocked_info.short_description = 'Engellenen'


@admin.register(MessageReport)
class MessageReportAdmin(admin.ModelAdmin):
    list_display = ['message_info', 'reporter_info', 'reason', 'is_resolved', 'reported_at']
    list_filter = ['reason', 'is_resolved', 'reported_at']
    search_fields = ['description', 'reporter__email', 'message__content']
    readonly_fields = ['reported_at']
    raw_id_fields = ['message', 'reporter']
    date_hierarchy = 'reported_at'
    
    fieldsets = (
        ('Şikayet Bilgileri', {
            'fields': ('message', 'reporter', 'reason', 'description')
        }),
        ('Durum', {
            'fields': ('is_resolved', 'resolved_at')
        }),
        ('Zaman Bilgileri', {
            'fields': ('reported_at',)
        }),
    )
    
    def message_info(self, obj):
        """Mesaj bilgisi"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:messages_message_change', args=[obj.message.pk]),
            str(obj.message)[:50]
        )
    message_info.short_description = 'Mesaj'
    
    def reporter_info(self, obj):
        """Şikayet eden kullanıcı"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:authentication_customuser_change', args=[obj.reporter.pk]),
            obj.reporter.get_full_name() or obj.reporter.email
        )
    reporter_info.short_description = 'Şikayet Eden'
    
    actions = ['mark_as_resolved', 'mark_as_unresolved']
    
    def mark_as_resolved(self, request, queryset):
        """Seçili şikayetleri çözümlenmiş olarak işaretle"""
        updated = queryset.filter(is_resolved=False).update(
            is_resolved=True, 
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} şikayet çözümlenmiş olarak işaretlendi.')
    mark_as_resolved.short_description = 'Seçili şikayetleri çözümlenmiş olarak işaretle'
    
    def mark_as_unresolved(self, request, queryset):
        """Seçili şikayetleri çözümlenmemiş olarak işaretle"""
        updated = queryset.filter(is_resolved=True).update(
            is_resolved=False, 
            resolved_at=None
        )
        self.message_user(request, f'{updated} şikayet çözümlenmemiş olarak işaretlendi.')
    mark_as_unresolved.short_description = 'Seçili şikayetleri çözümlenmemiş olarak işaretle'


# Admin site başlıkları
admin.site.site_header = 'Kuaförİlan Yönetim Paneli'
admin.site.site_title = 'Kuaförİlan Admin'
admin.site.index_title = 'Mesajlaşma Yönetimi'

