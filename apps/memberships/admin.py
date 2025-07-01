from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    SubscriptionPlan, 
    UserMembership, 
    MembershipPayment, 
    PlanFeature,
    MembershipUpgrade
)

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'plan_type', 'price', 'billing_cycle', 
        'max_job_posts', 'is_active', 'sort_order'
    ]
    list_filter = ['plan_type', 'billing_cycle', 'is_active']
    search_fields = ['name']
    ordering = ['sort_order', 'price']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'plan_type', 'price', 'billing_cycle', 'is_active', 'sort_order')
        }),
        ('Plan Özellikleri', {
            'fields': (
                'max_job_posts', 'can_highlight_jobs', 'can_feature_jobs',
                'cv_pool_access', 'priority_support', 'analytics_access'
            )
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('features')


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 0
    fields = ['feature_name', 'feature_description', 'is_included', 'sort_order']


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'plan', 'status', 'start_date', 
        'end_date', 'days_remaining_display', 'auto_renew'
    ]
    list_filter = ['status', 'plan', 'auto_renew', 'start_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at', 'days_remaining_display']
    
    fieldsets = (
        ('Kullanıcı & Plan', {
            'fields': ('user', 'plan')
        }),
        ('Tarihler', {
            'fields': ('start_date', 'end_date', 'days_remaining_display')
        }),
        ('Durum', {
            'fields': ('status', 'auto_renew')
        }),
        ('İstatistikler', {
            'fields': ('jobs_posted_this_period',)
        }),
        ('Sistem', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:authentication_customuser_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_link.short_description = 'Kullanıcı'
    
    def days_remaining_display(self, obj):
        days = obj.days_remaining()
        if days > 0:
            return format_html('<span style="color: green;">{} gün</span>', days)
        else:
            return format_html('<span style="color: red;">Süresi dolmuş</span>')
    days_remaining_display.short_description = 'Kalan Gün'


@admin.register(MembershipPayment)
class MembershipPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'plan', 'amount', 'currency', 
        'payment_method', 'status', 'payment_date', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'invoice_number', 'payment_provider_id'
    ]
    raw_id_fields = ['user', 'membership']
    readonly_fields = ['created_at', 'updated_at', 'payment_provider_response_display']
    
    fieldsets = (
        ('Ödeme Bilgileri', {
            'fields': ('user', 'membership', 'plan', 'amount', 'currency')
        }),
        ('Ödeme Yöntemi', {
            'fields': ('payment_method', 'status', 'payment_date')
        }),
        ('Sağlayıcı Bilgileri', {
            'fields': ('payment_provider_id', 'payment_provider_response_display'),
            'classes': ('collapse',)
        }),
        ('Fatura', {
            'fields': ('invoice_number',)
        }),
        ('Sistem', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:authentication_customuser_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_link.short_description = 'Kullanıcı'
    
    def payment_provider_response_display(self, obj):
        if obj.payment_provider_response:
            return format_html('<pre>{}</pre>', str(obj.payment_provider_response))
        return '-'
    payment_provider_response_display.short_description = 'Sağlayıcı Yanıtı'


@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ['plan', 'feature_name', 'is_included', 'sort_order']
    list_filter = ['plan', 'is_included']
    search_fields = ['feature_name', 'feature_description']
    ordering = ['plan', 'sort_order']


@admin.register(MembershipUpgrade)
class MembershipUpgradeAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 'current_plan', 'requested_plan', 
        'price_difference', 'status', 'requested_at'
    ]
    list_filter = ['status', 'current_plan', 'requested_plan', 'requested_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']
    readonly_fields = ['requested_at', 'processed_at', 'price_difference']
    
    fieldsets = (
        ('Yükseltme Talebi', {
            'fields': ('user', 'current_plan', 'requested_plan', 'price_difference')
        }),
        ('Durum', {
            'fields': ('status',)
        }),
        ('Tarihler', {
            'fields': ('requested_at', 'processed_at')
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:authentication_customuser_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_link.short_description = 'Kullanıcı'

# Admin site özelleştirmeleri
admin.site.site_header = "Kuaförİlan Yönetim Paneli"
admin.site.site_title = "Kuaförİlan Admin"
admin.site.index_title = "Yönetim Paneli"