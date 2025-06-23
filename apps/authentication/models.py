from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
import string


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
    phone = models.CharField(max_length=17, blank=True, unique=True, null=True, verbose_name='Telefon')  # +905551234567 formatı için
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
    phone_verified = models.BooleanField(default=False, verbose_name='Telefon Doğrulanmış')
    email_verified = models.BooleanField(default=False, verbose_name='Email Doğrulanmış')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')
    
    # Sosyal medya bilgileri
    google_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Google ID')
    linkedin_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='LinkedIn ID')
    
    # İstatistikler
    profile_views = models.IntegerField(default=0, verbose_name='Profil Görüntülenme')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Son Giriş IP')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_plan_active(self):
        """Plan aktif mi kontrol et"""
        if self.current_plan == 'free':
            return True
        return self.plan_end_date and self.plan_end_date > timezone.now()
    
    def format_phone(self):
        """Telefon numarasını formatla"""
        if self.phone:
            # +90 555 123 45 67 formatında döndür
            phone = self.phone.replace('+90', '').replace(' ', '')
            if len(phone) == 10:
                return f"+90 {phone[:3]} {phone[3:6]} {phone[6:8]} {phone[8:]}"
        return self.phone


class OTPVerification(models.Model):
    """OTP doğrulama modeli"""
    
    OTP_TYPE_CHOICES = [
        ('login', 'Giriş'),
        ('register', 'Kayıt'),
        ('password_reset', 'Şifre Sıfırlama'),
        ('phone_verify', 'Telefon Doğrulama'),
        ('email_verify', 'Email Doğrulama'),
    ]
    
    DELIVERY_METHOD_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
    ]
    
    # İlişkiler
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    
    # OTP bilgileri
    otp_code = models.CharField(max_length=6, verbose_name='OTP Kodu')
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES, verbose_name='OTP Tipi')
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHOD_CHOICES, verbose_name='Gönderim Yöntemi')
    
    # İletişim bilgileri
    phone_number = models.CharField(max_length=17, blank=True, verbose_name='Telefon Numarası')
    email_address = models.EmailField(blank=True, verbose_name='Email Adresi')
    
    # Durum bilgileri
    is_used = models.BooleanField(default=False, verbose_name='Kullanıldı')
    is_verified = models.BooleanField(default=False, verbose_name='Doğrulandı')
    attempts = models.IntegerField(default=0, verbose_name='Deneme Sayısı')
    max_attempts = models.IntegerField(default=3, verbose_name='Maksimum Deneme')
    
    # Zaman bilgileri
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')
    expires_at = models.DateTimeField(verbose_name='Son Geçerlilik')
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='Doğrulama Tarihi')
    
    # Güvenlik
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Adresi')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    
    class Meta:
        verbose_name = 'OTP Doğrulama'
        verbose_name_plural = 'OTP Doğrulamaları'
        ordering = ['-created_at']
    
    def __str__(self):
        target = self.phone_number or self.email_address
        return f"{self.otp_type} - {target} - {self.otp_code}"
    
    @classmethod
    def generate_otp(cls):
        """6 haneli OTP kodu üret"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """OTP süresi doldu mu?"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """OTP geçerli mi?"""
        return not self.is_used and not self.is_expired() and self.attempts < self.max_attempts
    
    def verify(self, entered_code):
        """OTP doğrula"""
        self.attempts += 1
        
        if self.attempts >= self.max_attempts:
            self.save()
            return False, "Maksimum deneme sayısına ulaştınız."
        
        if self.is_expired():
            self.save()
            return False, "OTP süresi doldu."
        
        if self.is_used:
            self.save()
            return False, "Bu OTP zaten kullanıldı."
        
        if entered_code == self.otp_code:
            self.is_used = True
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save()
            return True, "OTP başarıyla doğrulandı."
        else:
            self.save()
            return False, f"Yanlış OTP kodu. Kalan deneme: {self.max_attempts - self.attempts}"


class SocialAuthProvider(models.Model):
    """Sosyal medya sağlayıcı bilgileri"""
    
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('apple', 'Apple'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='social_providers')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, verbose_name='Sağlayıcı')
    provider_id = models.CharField(max_length=100, verbose_name='Sağlayıcı ID')
    provider_email = models.EmailField(blank=True, verbose_name='Sağlayıcı Email')
    
    # Ek bilgiler
    access_token = models.TextField(blank=True, verbose_name='Access Token')
    refresh_token = models.TextField(blank=True, verbose_name='Refresh Token')
    token_expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Token Süresi')
    
    # Meta bilgiler
    profile_data = models.JSONField(default=dict, verbose_name='Profil Verisi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Bağlama Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')
    
    class Meta:
        verbose_name = 'Sosyal Medya Sağlayıcı'
        verbose_name_plural = 'Sosyal Medya Sağlayıcıları'
        unique_together = ('user', 'provider')
    
    def __str__(self):
        return f"{self.user.email} - {self.provider}"


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
    city = models.CharField(max_length=50, blank=True, verbose_name='Şehir')
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
        default='1-5',
        verbose_name='Şirket Büyüklüğü'
    )
    establishment_year = models.IntegerField(default=2024, verbose_name='Kuruluş Yılı')
    
    # İletişim bilgileri
    city = models.CharField(max_length=50, blank=True, verbose_name='Şehir')
    district = models.CharField(max_length=50, blank=True, verbose_name='İlçe')
    address = models.TextField(blank=True, verbose_name='Adres')
    website = models.URLField(blank=True, verbose_name='Web Sitesi')
    
    # Yetkili kişi
    contact_person = models.CharField(max_length=100, blank=True, verbose_name='Yetkili Kişi')
    contact_phone = models.CharField(max_length=15, blank=True, verbose_name='Yetkili Telefon')
    
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
    
    def __str__(self):
        return f"{self.company_name} - {self.contact_person}"
        
