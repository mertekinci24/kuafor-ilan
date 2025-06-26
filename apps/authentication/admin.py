from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTPVerification, SocialAuthProvider, LoginHistory

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'get_full_name', 'user_type', 'current_plan', 'is_verified', 'date_joined')
    list_filter = ('user_type', 'current_plan', 'is_verified', 'email_verified', 'phone_verified')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Kullanıcı Bilgileri', {
            'fields': ('phone', 'user_type', 'current_plan', 'plan_start_date', 'plan_end_date')
        }),
        ('Doğrulama', {
            'fields': ('is_verified', 'email_verified', 'phone_verified')
        }),
        ('İstatistikler', {
            'fields': ('profile_views', 'last_login_ip')
        }),
        ('Ayarlar', {
            'fields': ('email_notifications', 'sms_notifications', 'marketing_emails')
        }),
    )

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('otp_code', 'user', 'otp_type', 'delivery_method', 'is_used', 'created_at')
    list_filter = ('otp_type', 'delivery_method', 'is_used', 'is_expired')
    search_fields = ('user__email', 'phone_number', 'email_address')

@admin.register(SocialAuthProvider)
class SocialAuthProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'provider_email', 'created_at')
    list_filter = ('provider',)
    search_fields = ('user__email', 'provider_email')

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_method', 'is_successful', 'ip_address', 'created_at')
    list_filter = ('login_method', 'is_successful')
    search_fields = ('user__email', 'ip_address')
    
