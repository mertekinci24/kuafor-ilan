from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from apps.core.models import TimeStampedModel
import random
import string


class CustomUser(AbstractUser):
    """Özelleştirilmiş kullanıcı modeli"""
    
    USER_TYPE_CHOICES = (
        ('jobseeker', 'İş Arayan'),
        ('business', 'İş Veren'),
        ('admin', 'Yönetici'),
    )
    
    PLAN_CHOICES = (
        ('free', 'Ücretsiz'),
        ('basic', 'Temel'),
        ('premium', 'Premium'),
        ('enterprise', 'Kurumsal'),
    )
    
    # Basic Info
    email = models.EmailField(unique=True, verbose_name='E-posta')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Telefon numarası +905551234567 formatında olmalıdır."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True,
        verbose_name='Telefon'
    )
    
    # User Type & Plan
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='jobseeker',
        verbose_name='Kullanıcı Tipi'
    )
    current_plan = models.CharField(
        max_length=20, 
        choices=PLAN_CHOICES, 
        default='free',
        verbose_name='Mevcut Plan'
    )
    plan_start_date = models.DateTimeField(null=True, blank=True)
    plan_end_date = models.DateTimeField(null=True, blank=True)
    
    # Verification Status
    is_verified = models.BooleanField(default=False, verbose_name='Doğrulanmış')
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Statistics
    profile_views = models.PositiveIntegerField(default=0)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    def get_avatar_initial(self):
        """Avatar için baş harf"""
        if self.first_name:
            return self.first_name[0].upper()
        return self.email[0].upper()
    
    def is_premium_user(self):
        """Premium kullanıcı kontrolü"""
        return self.current_plan in ['premium', 'enterprise']
    
    def days_until_plan_expires(self):
        """Plan bitimine kalan gün"""
        if self.plan_end_date:
            days = (self.plan_end_date - timezone.now()).days
            return max(0, days)
        return None


class JobSeekerProfile(TimeStampedModel):
    """İş arayan profili"""
    
    EXPERIENCE_CHOICES = (
        (0, 'Yeni başlayan'),
        (1, '1 yıl'),
        (2, '2 yıl'),
        (3, '3 yıl'),
        (4, '4 yıl'),
        (5, '5 yıl'),
        (6, '6-10 yıl'),
        (10, '10+ yıl'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='jobseeker_profile')
    
    # Personal Info
    birth_date = models.DateField(null=True, blank=True, verbose_name='Doğum Tarihi')
    bio = models.TextField(blank=True, verbose_name='Hakkımda')
    
    # Location
    city = models.CharField(max_length=50, verbose_name='Şehir')
    district = models.CharField(max_length=50, blank=True, verbose_name='İlçe')
    address = models.TextField(blank=True, verbose_name='Adres')
    
    # Professional Info
    experience_years = models.PositiveIntegerField(
        choices=EXPERIENCE_CHOICES, 
        default=0, 
        verbose_name='Deneyim'
    )
    skills = models.TextField(
        blank=True, 
        help_text='Virgül ile ayırarak yazın',
        verbose_name='Yetenekler'
    )
    portfolio_url = models.URLField(blank=True, verbose_name='Portfolio')
    linkedin_url = models.URLField(blank=True, verbose_name='LinkedIn')
    
    # Files
    cv_file = models.FileField(upload_to='cvs/', blank=True, verbose_name='CV')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, verbose_name='Profil Fotoğrafı')
    certificates = models.FileField(upload_to='certificates/', blank=True, verbose_name='Sertifikalar')
    
    # Status
    is_available = models.BooleanField(default=True, verbose_name='İş Arıyor')
    expected_salary_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='Beklenen Maaş (Min)')
    expected_salary_max = models.PositiveIntegerField(null=True, blank=True, verbose_name='Beklenen Maaş (Max)')
    
    # Statistics
    total_applications = models.PositiveIntegerField(default=0)
    successful_applications = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'İş Arayan Profili'
        verbose_name_plural = 'İş Arayan Profilleri'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - İş Arayan"
    
    def get_skills_list(self):
        """Yetenekleri liste olarak döndür"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
        return []
    
    def get_experience_display_text(self):
        """Deneyimi text olarak döndür"""
        exp_dict = dict(self.EXPERIENCE_CHOICES)
        return exp_dict.get(self.experience_years, 'Belirtilmemiş')


class BusinessProfile(TimeStampedModel):
    """İş veren profili"""
    
    COMPANY_SIZE_CHOICES = (
        ('1-10', '1-10 çalışan'),
        ('11-50', '11-50 çalışan'),
        ('51-200', '51-200 çalışan'),
        ('201-500', '201-500 çalışan'),
        ('500+', '500+ çalışan'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='business_profile')
    
    # Company Info
    company_name = models.CharField(max_length=100, verbose_name='Şirket Adı')
    company_description = models.TextField(blank=True, verbose_name='Şirket Açıklaması')
    company_size = models.CharField(
        max_length=20, 
        choices=COMPANY_SIZE_CHOICES, 
        blank=True,
        verbose_name='Şirket Büyüklüğü'
    )
    establishment_year = models.PositiveIntegerField(null=True, blank=True, verbose_name='Kuruluş Yılı')
    
    # Contact Info
    city = models.CharField(max_length=50, verbose_name='Şehir')
    district = models.CharField(max_length=50, blank=True, verbose_name='İlçe')
    address = models.TextField(verbose_name='Adres')
    website = models.URLField(blank=True, verbose_name='Website')
    
    # Contact Person
    contact_person = models.CharField(max_length=100, blank=True, verbose_name='İletişim Kişisi')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='İletişim Telefonu')
    
    # Verification
    is_verified = models.BooleanField(default=False, verbose_name='Doğrulanmış Şirket')
    verification_documents = models.FileField(
        upload_to='verifications/', 
        blank=True, 
        verbose_name='Doğrulama Belgeleri'
    )
    
    # Images
    logo = models.ImageField(upload_to='company_logos/', blank=True, verbose_name='Logo')
    cover_image = models.ImageField(upload_to='company_covers/', blank=True, verbose_name='Kapak Fotoğrafı')
    
    # Statistics
    total_job_posts = models.PositiveIntegerField(default=0)
    active_job_posts = models.PositiveIntegerField(default=0)
    total_applications_received = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'İş Veren Profili'
        verbose_name_plural = 'İş Veren Profilleri'
    
    def __str__(self):
        return f"{self.company_name} - {self.user.get_full_name()}"


class OTPVerification(TimeStampedModel):
    """OTP doğrulama sistemi"""
    
    OTP_TYPE_CHOICES = (
        ('login', 'Giriş'),
        ('register', 'Kayıt'),
        ('password_reset', 'Şifre Sıfırlama'),
        ('phone_verify', 'Telefon Doğrulama'),
        ('email_verify', 'Email Doğrulama'),
    )
    
    DELIVERY_METHOD_CHOICES = (
        ('sms', 'SMS'),
        ('email', 'Email'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES)
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHOD_CHOICES)
    
    # Contact Info
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    
    # Status
    is_used = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Security
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'OTP Doğrulama'
        verbose_name_plural = 'OTP Doğrulamalar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP {self.otp_code} - {self.get_otp_type_display()}"
    
    @staticmethod
    def generate_otp():
        """6 haneli OTP üret"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        """OTP geçerli mi?"""
        return not self.is_used and not self.is_expired and timezone.now() < self.expires_at
    
    def verify(self, provided_otp):
        """OTP doğrula"""
        self.attempts += 1
        self.save()
        
        if self.attempts > self.max_attempts:
            self.is_expired = True
            self.save()
            return False, "Çok fazla hatalı deneme. OTP geçersiz."
        
        if not self.is_valid():
            return False, "OTP süresi dolmuş veya kullanılmış."
        
        if self.otp_code != provided_otp:
            return False, "OTP kodu hatalı."
        
        # Başarılı doğrulama
        self.is_used = True
        self.verified_at = timezone.now()
        self.save()
        
        return True, "OTP başarıyla doğrulandı."
    
    def mark_expired(self):
        """OTP'yi süresi dolmuş olarak işaretle"""
        self.is_expired = True
        self.save()


class SocialAuthProvider(TimeStampedModel):
    """Sosyal medya authentication sağlayıcıları"""
    
    PROVIDER_CHOICES = (
        ('google', 'Google'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='social_providers')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_id = models.CharField(max_length=100)
    provider_email = models.EmailField(blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    profile_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Sosyal Medya Bağlantısı'
        verbose_name_plural = 'Sosyal Medya Bağlantıları'
        unique_together = ('user', 'provider')
    
    def __str__(self):
        return f"{self.user.email} - {self.get_provider_display()}"


class LoginHistory(TimeStampedModel):
    """Giriş geçmişi"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    is_successful = models.BooleanField(default=True)
    login_method = models.CharField(
        max_length=20,
        choices=[
            ('password', 'Şifre'),
            ('otp_sms', 'OTP SMS'),
            ('otp_email', 'OTP Email'),
            ('google', 'Google'),
            ('linkedin', 'LinkedIn'),
        ],
        default='password'
    )
    location = models.CharField(max_length=100, blank=True)  # IP'den çözümlenecek
    device_info = models.CharField(max_length=200, blank=True)
    
    class Meta:
        verbose_name = 'Giriş Geçmişi'
        verbose_name_plural = 'Giriş Geçmişi'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.created_at}"
        
