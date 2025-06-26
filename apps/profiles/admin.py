from django.contrib import admin
from django.utils.html import format_html
from .models import JobSeekerProfile, BusinessProfile


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'experience_years', 'is_available', 'total_applications', 'profile_completion')
    list_filter = ('city', 'experience_years', 'is_available', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'city')
    readonly_fields = ('created_at', 'updated_at', 'total_applications', 'successful_applications')
    
    fieldsets = (
        ('Kullanıcı', {'fields': ('user',)}),
        ('Kişisel Bilgiler', {'fields': ('birth_date', 'bio')}),
        ('Konum', {'fields': ('city', 'district', 'address')}),
        ('Profesyonel Bilgiler', {'fields': ('experience_years', 'skills', 'portfolio_url', 'linkedin_url')}),
        ('Maaş Beklentisi', {'fields': ('expected_salary_min', 'expected_salary_max')}),
        ('Belgeler', {'fields': ('cv_file', 'profile_image', 'certificates')}),
        ('Durum', {'fields': ('is_available',)}),
        ('İstatistikler', {'fields': ('total_applications', 'successful_applications')}),
        ('Tarihler', {'fields': ('created_at', 'updated_at')}),
    )
    
    actions = ['mark_available', 'mark_unavailable']
    
    def profile_completion(self, obj):
        completion = 0
        total_fields = 10
        
        if obj.birth_date: completion += 1
        if obj.city: completion += 1
        if obj.address: completion += 1
        if obj.bio: completion += 1
        if obj.portfolio_url: completion += 1
        if obj.cv_file: completion += 1
        if obj.skills: completion += 1
        if obj.experience_years: completion += 1
        if obj.profile_image: completion += 1
        if obj.expected_salary_min: completion += 1
        
        percentage = (completion / total_fields) * 100
        color = 'green' if percentage >= 70 else 'orange' if percentage >= 40 else 'red'
        
        return format_html(
            '<span style="color: {};">{:.0f}%</span>',
            color,
            percentage
        )
    profile_completion.short_description = 'Profil Tamamlanma'
    
    def mark_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} profil iş arıyor olarak işaretlendi.')
    mark_available.short_description = 'İş arıyor olarak işaretle'
    
    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} profil iş aramıyor olarak işaretlendi.')
    mark_unavailable.short_description = 'İş aramıyor olarak işaretle'


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
        ('Görseller', {'fields': ('logo', 'cover_image')}),
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
    
