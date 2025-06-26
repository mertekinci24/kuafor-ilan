from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from .models import (
    NotificationType, 
    Notification, 
    UserNotificationSettings, 
    NotificationTemplate, 
    NotificationBatch
)


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'icon_display', 'color_display', 'is_active', 'send_email', 'send_sms', 'send_push']
    list_filter = ['is_active', 'send_email', 'send_sms', 'send_push', 'created_at']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'send_email', 'send_sms', 'send_push']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('code', 'name', 'description')
        }),
        ('Görünüm', {
            'fields': ('icon', 'color')
        }),
        ('Gönderim Ayarları', {
            'fields': ('send_email', 'send_sms', 'send_push', 'is_active')
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def icon_display(self, obj):
        """İkon gösterimi"""
        return format_html('<i class="{}" style="font-size: 16px;"></i>', obj.icon)
    icon_display.short_description = 'İkon'
    
    def color_display(self, obj):
        """Renk gösterimi"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div>',
            obj.color
        )
    color_display.short_description = 'Renk'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient_info', 'title_short', 'notification_type', 'priority_display', 'is_read', 'is_sent', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'is_sent', 'created_at']
    search_fields = ['title', 'message', 'recipient__email', 'recipient__first_name', 'recipient__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'read_at', 'sent_at', 'delivered_at']
    raw_id_fields = ['recipient', 'content_type']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alıcı ve Tür', {
            'fields': ('recipient', 'notification_type', 'priority')
        }),
        ('İçerik', {
            'fields': ('title', 'message', 'short_message')
        }),
        ('İlgili Nesne', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Eylem', {
            'fields': ('action_url', 'action_text'),
            'classes': ('collapse',)
        }),
        ('Durum', {
            'fields': ('is_read', 'read_at', 'is_sent', 'sent_at', 'is_delivered', 'delivered_at')
        }),
        ('Email/SMS Durumu', {
            'fields': ('email_sent', 'email_sent_at', 'sms_sent', 'sms_sent_at'),
            'classes': ('collapse',)
        }),
        ('Zaman Bilgileri', {
            'fields': ('id', 'created_at', 'updated_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    def recipient_info(self, obj):
        """Alıcı bilgisi"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:authentication_customuser_change', args=[obj.recipient.pk]),
            obj.recipient.get_full_name() or obj.recipient.email
        )
    recipient_info.short_description = 'Alıcı'
    
    def title_short(self, obj):
        """Kısa başlık"""
        if len(obj.title) > 50:
            return f"{obj.title[:50]}..."
        return obj.title
    title_short.short_description = 'Başlık'
    
    def priority_display(self, obj):
        """Öncelik gösterimi"""
        colors = {
            'low': '#6c757d',
            'normal': '#007bff',
            'high': '#ffc107',
            'urgent': '#dc3545',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.priority, '#007bff'),
            obj.get_priority_display()
        )
    priority_display.short_description = 'Öncelik'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'notification_type')
    
    actions = ['mark_as_read', 'mark_as_sent', 'delete_selected_notifications']
    
    def mark_as_read(self, request, queryset):
        """Seçili bildirimleri okundu olarak işaretle"""
        updated = 0
        for notification in queryset.filter(is_read=False):
            notification.mark_as_read()
            updated += 1
        self.message_user(request, f'{updated} bildirim okundu olarak işaretlendi.')
    mark_as_read.short_description = 'Seçili bildirimleri okundu olarak işaretle'
    
    def mark_as_sent(self, request, queryset):
        """Seçili bildirimleri gönderildi olarak işaretle"""
        updated = 0
        for notification in queryset.filter(is_sent=False):
            notification.mark_as_sent()
            updated += 1
        self.message_user(request, f'{updated} bildirim gönderildi olarak işaretlendi.')
    mark_as_sent.short_description = 'Seçili bildirimleri gönderildi olarak işaretle'
    
    def delete_selected_notifications(self, request, queryset):
        """Seçili bildirimleri sil"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} bildirim silindi.')
    delete_selected_notifications.short_description = 'Seçili bildirimleri sil'


@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user_info', 'email_notifications', 'push_notifications', 'quiet_hours_enabled', 'updated_at']
    list_filter = ['email_notifications', 'sms_notifications', 'push_notifications', 'quiet_hours_enabled', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Kullanıcı', {
            'fields': ('user',)
        }),
        ('Genel Ayarlar', {
            'fields': ('email_notifications', 'sms_notifications', 'push_notifications')
        }),
        ('İş Bildirimleri', {
            'fields': ('job_applications', 'job_matches', 'job_deadlines')
        }),
        ('Mesaj Bildirimleri', {
            'fields': ('new_messages', 'message_read_receipts')
        }),
        ('Sosyal Bildirimler', {
            'fields': ('post_interactions', 'new_followers')
        }),
        ('Sistem Bildirimleri', {
            'fields': ('system_updates', 'security_alerts')
        }),
        ('Pazarlama Bildirimleri', {
            'fields': ('promotions', 'newsletters')
        }),
        ('Sessiz Saatler', {
            'fields': ('quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end')
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_info(self, obj):
        """Kullanıcı bilgisi"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:authentication_customuser_change', args=[obj.user.pk]),
            obj.user.get_full_name() or obj.user.email
        )
    user_info.short_description = 'Kullanıcı'


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_active', 'created_at']
    search_fields = ['name', 'title_template', 'message_template']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('notification_type', 'name', 'is_active')
        }),
        ('App İçi Şablon', {
            'fields': ('title_template', 'message_template')
        }),
        ('Email Şablonu', {
            'fields': ('email_subject_template', 'email_body_template'),
            'classes': ('collapse',)
        }),
        ('SMS Şablonu', {
            'fields': ('sms_template',),
            'classes': ('collapse',)
        }),
        ('Değişkenler', {
            'fields': ('variables',),
            'classes': ('collapse',)
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationBatch)
class NotificationBatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'total_recipients', 'sent_count', 'is_sent', 'scheduled_at', 'created_at']
    list_filter = ['notification_type', 'is_sent', 'scheduled_at', 'created_at']
    search_fields = ['name', 'title', 'message']
    readonly_fields = ['sent_count', 'failed_count', 'sent_at', 'created_at']
    raw_id_fields = ['created_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'notification_type', 'created_by')
        }),
        ('Hedef Kitle', {
            'fields': ('recipient_filter', 'total_recipients')
        }),
        ('İçerik', {
            'fields': ('title', 'message', 'action_url', 'action_text')
        }),
        ('Durum', {
            'fields': ('is_sent', 'sent_count', 'failed_count', 'sent_at')
        }),
        ('Zamanlama', {
            'fields': ('scheduled_at',)
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('notification_type', 'created_by')


# Admin site özelleştirmeleri
class NotificationAdminSite(admin.AdminSite):
    site_header = 'Bildirim Yönetimi'
    site_title = 'Bildirimler Admin'
    index_title = 'Bildirim Sistemı Yönetimi'


# Özel admin site oluştur
notification_admin_site = NotificationAdminSite(name='notification_admin')
notification_admin_site.register(NotificationType, NotificationTypeAdmin)
notification_admin_site.register(Notification, NotificationAdmin)
notification_admin_site.register(UserNotificationSettings, UserNotificationSettingsAdmin)
notification_admin_site.register(NotificationTemplate, NotificationTemplateAdmin)
notification_admin_site.register(NotificationBatch, NotificationBatchAdmin)


# İstatistik görünümü için özel admin action
def notification_stats(modeladmin, request, queryset):
    """Bildirim istatistikleri"""
    total = queryset.count()
    read = queryset.filter(is_read=True).count()
    unread = total - read
    sent = queryset.filter(is_sent=True).count()
    
    modeladmin.message_user(
        request,
        f'Toplam: {total}, Okundu: {read}, Okunmadı: {unread}, Gönderildi: {sent}'
    )

notification_stats.short_description = 'Seçili bildirimlerin istatistiklerini göster'

# Action'ı ekle
NotificationAdmin.actions.append(notification_stats)

