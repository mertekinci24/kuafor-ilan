from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, JobSeekerProfile, BusinessProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'get_full_name', 'user_type', 'current_plan', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('user_type', 'current_plan', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    readonly_fields = ('date_joined', 'last_login', 'profile_views')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Hesap Bilgileri', {'fields': ('user_type', 'current_plan', 'plan_start_date', 'plan_end_date')}),
        ('Durum', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser')}),
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
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email
    get_full_name.short_description = 'Ad Soyad'


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'experience_years', 'total_applications', 'profile_completion')
    list_filter = ('city', 'experience_years', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'city')
    readonly_fields = ('created_at', 'updated_at', 'total_applications', 'successful_applications')
    
    fieldsets = (
        ('Kullanıcı', {'fields': ('user',)}),
        ('Kişisel Bilgiler', {'fields': ('birth_date', 'city', 'district', 'address')}),
        ('Profesyonel Bilgiler', {'fields': ('experience_years', 'skills', 'bio', 'portfolio_url')}),
        ('Belgeler', {'fields': ('cv_file', 'certificates')}),
        ('İstatistikler', {'fields': ('total_applications', 'successful_applications')}),
        ('Tarihler', {'fields': ('created_at', 'updated_at')}),
    )
    
    def profile_completion(self, obj):
        completion = 0
        total_fields = 8
        
        if obj.birth_date: completion += 1
        if obj.city: completion += 1
        if obj.address: completion += 1
        if obj.bio: completion += 1
        if obj.portfolio_url: completion += 1
        if obj.cv_file: completion += 1
        if obj.skills: completion += 1
        if obj.experience_years: completion += 1
        
        percentage = (completion / total_fields) * 100
        color = 'green' if percentage >= 70 else 'orange' if percentage >= 40 else 'red'
        
        return format_html(
            '<span style="color: {};">{:.0f}%</span>',
            color,
            percentage
        )
    profile_completion.short_description = 'Profil Tamamlanma'


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_person', 'city', 'company_size', 'is_verified', 'total_job_posts')
    list_filter = ('city', 'company_size', 'is_verified', 'establishment_year', 'created_at')
    search_fields = ('company_name', 'contact_person', 'user__email', 'city')
    readonly_fields = ('created_at', 'updated_at', 'total_job_posts', 'active_job_posts', 'total_applications_received')
    
    fieldsets = (
        ('Kullanıcı', {'fields': ('user',)}),
        ('Şirket Bilgileri', {'fields': ('company_name', 'company_description', 'company_size', 'establishment_year')}),
        ('İletişim Bilgileri', {'fields': ('city', 'district', 'address', 'website')}),
        ('Yetkili Kişi', {'fields': ('contact_person', 'contact_phone')}),
        ('Doğrulama', {'fields': ('is_verified', 'verification_documents')}),
        ('İstatistikler', {'fields': ('total_job_posts', 'active_job_posts', 'total_applications_received')}),
        ('Tarihler', {'fields': ('created_at', 'updated_at')}),
    )
    
    actions = ['verify_companies', 'unverify_companies']
    
    def verify_companies(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} şirket doğrulandı.')
    verify_companies.short_description = 'Seçili şirketleri doğrula'
    
    def unverify_companies(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} şirketin doğrulaması kaldırıldı.')
    unverify_companies.short_description = 'Seçili şirketlerin doğrulamasını kaldır'
    
