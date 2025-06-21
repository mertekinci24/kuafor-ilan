from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    """Özel kullanıcı modeli - JobSeeker ve Business için"""
    
    USER_TYPE_CHOICES = [
        ('jobseeker', 'İş Arayan'),
        ('business', 'İş Veren'),
    ]
    
    PLAN_CHOICES = [
        ('free', 'Ücretsiz'),
        ('pro', 'Pro'),
        ('business', 'İşletme'),
    ]
    
    # Temel bilgiler
    email = models.EmailField(unique=True, verbose_name='E-posta')
    phone = models.CharField(max_length=15, blank=True, verbose_name='Telefon')
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='jobseeker',
        verbose_name='Kullanıcı Tipi'
    )
    
    # Plan bilgileri
    current_plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='free',
        verbose_name='Mevcut Plan'
    )
    plan_start_date = models.DateTimeField(default=timezone.now, verbose_name='Plan Başlangıç')
    plan_end_date = models.DateTimeField(null=True, blank=True, verbose_name='Plan Bitiş')
    
    # Profil durumu
    is_verified = models.BooleanField(default=False, verbose_name='Doğrulanmış')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')
    
    # İstatistikler
    profile_views = models.IntegerField(default=0, verbose_name='Profil Görüntülenme')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Son Giriş IP')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        db_table = 'auth_users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_plan_active(self):
        """Plan aktif mi kontrol et"""
        if self.current_plan == 'free':
            return True
        return self.plan_end_date and self.plan_end_date > timezone.now()


class JobSeekerProfile(models.Model):
    """İş arayan profil detayları"""
    
    EXPERIENCE_CHOICES = [
        ('beginner', 'Yeni başlayan'),
        ('1-2', '1-2 yıl'),
        ('3-5', '3-5 yıl'),
        ('6-10', '6-10 yıl'),
        ('10+', '10+ yıl'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='jobseeker_profile')
    
    # Kişisel bilgiler
    birth_date = models.DateField(null=True, blank=True, verbose_name='Doğum Tarihi')
    city = models.CharField(max_length=50, verbose_name='Şehir')
    district = models.CharField(max_length=50, blank=True, verbose_name='İlçe')
    address = models.TextField(blank=True, verbose_name='Adres')
    
    # Profesyonel bilgiler
    experience_years = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='beginner',
        verbose_name='Deneyim'
    )
    skills = models.JSONField(default=list, verbose_name='Yetenekler')
    bio = models.TextField(blank=True, verbose_name='Hakkında')
    portfolio_url = models.URLField(blank=True, verbose_name='Portföy URL')
    
    # CV ve belgeler
    cv_file = models.FileField(upload_to='cvs/', blank=True, verbose_name='CV Dosyası')
    certificates = models.JSONField(default=list, verbose_name='Sertifikalar')
    
    # İstatistikler
    total_applications = models.IntegerField(default=0, verbose_name='Toplam Başvuru')
    successful_applications = models.IntegerField(default=0, verbose_name='Başarılı Başvuru')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'İş Arayan Profili'
        verbose_name_plural = 'İş Arayan Profilleri'
        db_table = 'jobseeker_profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - İş Arayan"


class BusinessProfile(models.Model):
    """İş veren profil detayları"""
    
    COMPANY_SIZE_CHOICES = [
        ('1-5', '1-5 kişi'),
        ('6-20', '6-20 kişi'),
        ('21-50', '21-50 kişi'),
        ('51-100', '51-100 kişi'),
        ('100+', '100+ kişi'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='business_profile')
    
    # Şirket bilgileri
    company_name = models.CharField(max_length=200, verbose_name='Şirket Adı')
    company_description = models.TextField(blank=True, verbose_name='Şirket Açıklaması')
    company_size = models.CharField(
        max_length=20,
        choices=COMPANY_SIZE_CHOICES,
        verbose_name='Şirket Büyüklüğü'
    )
    establishment_year = models.IntegerField(verbose_name='Kuruluş Yılı')
    
    # İletişim bilgileri
    city = models.CharField(max_length=50, verbose_name='Şehir')
    district = models.CharField(max_length=50, blank=True, verbose_name='İlçe')
    address = models.TextField(verbose_name='Adres')
    website = models.URLField(blank=True, verbose_name='Web Sitesi')
    
    # Yetkili kişi
    contact_person = models.CharField(max_length=100, verbose_name='Yetkili Kişi')
    contact_phone = models.CharField(max_length=15, verbose_name='Yetkili Telefon')
    
    # İstatistikler
    total_job_posts = models.IntegerField(default=0, verbose_name='Toplam İlan')
    active_job_posts = models.IntegerField(default=0, verbose_name='Aktif İlan')
    total_applications_received = models.IntegerField(default=0, verbose_name='Alınan Başvuru')
    
    # Doğrulama
    is_verified = models.BooleanField(default=False, verbose_name='Doğrulanmış Şirket')
    verification_documents = models.JSONField(default=list, verbose_name='Doğrulama Belgeleri')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'İş Veren Profili'
        verbose_name_plural = 'İş Veren Profilleri'
        db_table = 'business_profiles'
    
    def __str__(self):
        return f"{self.company_name} - {self.contact_person}"
        
