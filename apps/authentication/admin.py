from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, OTPVerification, SocialAuthProvider, LoginHistory


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'get_full_name', 'user_type', 'current_plan', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('user_type', 'current_plan', 'is_verified', 'email_verified', 'phone_verified', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    readonly_fields = ('date_joined', 'last_login', 'profile_views', 'last_login_ip')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Hesap Bilgileri', {'fields': ('user_type', 'current_plan', 'plan_start_date', 'plan_end_date')}),
        ('Doğrulama', {'fields': ('is_verified', 'email_verified', 'phone_verified')}),
        ('Durum', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Bildirim Ayarları', {'fields': ('email_notifications', 'sms_notifications', 'marketing_emails')}),
        ('İstatistikler', {'fields': ('profile_views', 'last_login_ip')}),
        ('Tarihler', {'fields': ('date_joined', 'last_login')}),
        ('Yetkiler', {'fields': ('groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    
    actions = ['verify_users', 'unverify_users', 'upgrade_to_premium']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email
    get_full_name.short_description = 'Ad Soyad'
    
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} kullanıcı doğrulandı.')
    verify_users.short_description = 'Seçili kullanıcıları doğrula'
    
    def unverify_users(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} kullanıcının doğrulaması kaldırıldı.')
    unverify_users.short_description = 'Seçili kullanıcıların doğrulamasını kaldır'
    
    def upgrade_to_premium(self, request, queryset):
        updated = queryset.update(current_plan='premium')
        self.message_user(request, f'{updated} kullanıcı premium plana yükseltildi.')
    upgrade_to_premium.short_description = 'Seçili kullanıcıları premium yap'


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('otp_code', 'user_info', 'otp_type', 'delivery_method', 'is_used', 'is_expired', 'attempts', 'created_at')
    list_filter = ('otp_type', 'delivery_method', 'is_used', 'is_expired', 'created_at')
    search_fields = ('user__email', 'phone_number', 'email_address', 'otp_code')
    readonly_fields = ('created_at', 'updated_at', 'verified_at')
    
    fieldsets = (
        ('OTP Bilgileri', {'fields': ('otp_code', 'otp_type', 'delivery_method')}),
        ('Kullanıcı', {'fields': ('user', 'phone_number', 'email_address')}),
        ('Durum', {'fields': ('is_used', 'is_expired', 'expires_at', 'verified_at')}),
        ('Güvenlik', {'fields': ('attempts', 'max_attempts', 'ip_address', 'user_agent')}),
        ('Tarihler', {'fields': ('created_at', 'updated_at')}),
    )
    
    def user_info(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.email})"
        return obj.email_address or obj.phone_number
    user_info.short_description = 'Kullanıcı'


@admin.register(SocialAuthProvider)
class SocialAuthProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'provider_email', 'created_at')
    list_filter = ('provider', 'created_at')
    search_fields = ('user__email', 'provider_email', 'provider_id')
    readonly_fields = ('created_at', 'updated_at', 'profile_data')
    
    fieldsets = (
        ('Kullanıcı', {'fields': ('user',)}),
        ('Sağlayıcı Bilgileri', {'fields': ('provider', 'provider_id', 'provider_email')}),
        ('Token Bilgileri', {'fields': ('access_token', 'refresh_token')}),
        ('Profil Verisi', {'fields': ('profile_data',)}),
        ('Tarihler', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_method', 'is_successful', 'ip_address', 'location', 'created_at')
    list_filter = ('login_method', 'is_successful', 'created_at')
    search_fields = ('user__email', 'ip_address', 'location', 'device_info')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Kullanıcı', {'fields': ('user',)}),
        ('Giriş Bilgileri', {'fields': ('login_method', 'is_successful')}),
        ('Teknik Bilgiler', {'fields': ('ip_address', 'user_agent', 'device_info')}),
        ('Konum', {'fields': ('location',)}),
        ('Tarihler', {'fields': ('created_at', 'updated_at')}),
    )
    
    def has_add_permission(self, request):
        return False  # Giriş geçmişi manuel eklenmez
