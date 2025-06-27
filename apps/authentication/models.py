from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from apps.core.models import TimeStampedModel # Bu import'un projenizde mevcut olduğunu varsayıyorum
import random
import string

class CustomUserManager(BaseUserManager):
    """
    CustomUser modeli için özel kullanıcı yöneticisi.
    E-posta ve/veya telefon numarası ile kullanıcı oluşturmayı destekler.
    """
    def _create_user(self, email, phone, password, **extra_fields):
        """
        E-posta ve/veya telefon numarası ile kullanıcı oluşturan ve kaydeden temel metod.
        """
        if not email and not phone:
            raise ValueError('Email veya telefon numarası alanı boş bırakılamaz.')

        user = self.model(email=self.normalize_email(email) if email else None, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, phone=None, password=None, **extra_fields):
        """
        Normal bir kullanıcı oluşturur ve kaydeder.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_verified', False) # Varsayılan olarak doğrulanmamış
        extra_fields.setdefault('email_verified', False)
        extra_fields.setdefault('phone_verified', False)

        # AbstractUser'dan gelen 'username' REQUIRED_FIELDS'da olduğu için burada da kabul etmeliyiz.
        # Ancak CustomUser modelindeki username alanı null=True, blank=True olmadığı için
        # create_user ve create_superuser çağrılarında username mutlaka sağlanmalıdır.
        user = self._create_user(email, phone, password, username=username, **extra_fields)
        return user

    def create_superuser(self, username, email=None, phone=None, password=None, **extra_fields):
        """
        Bir süper kullanıcı oluşturur ve kaydeder.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True) # Süper kullanıcılar varsayılan olarak doğrulanmış olmalı
        extra_fields.setdefault('email_verified', True)
        extra_fields.setdefault('phone_verified', True)


        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # AbstractUser'dan gelen 'username' REQUIRED_FIELDS'da olduğu için burada da kabul etmeliyiz.
        user = self._create_user(email, phone, password, username=username, **extra_fields)
        return user


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
    # email alanı zaten AbstractUser'da bulunur, ancak unique=True yapmak ve verbose_name eklemek için override edildi.
    email = models.EmailField(unique=True, verbose_name='E-posta', null=True, blank=True) # Email artık opsiyonel olabilir eğer telefonla giriş yapılacaksa

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Telefon numarası +905551234567 formatında olmalıdır."
    )
    phone = models.CharField( # phone_number yerine 'phone' olarak güncelledik
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        verbose_name='Telefon'
    )
    # is_phone_verified
    is_phone_verified = models.BooleanField(default=False, verbose_name='Telefon Doğrulandı mı?')

    # username alanı AbstractUser'dan gelir. Modelinizdeki tanımını kaldırdım
    # çünkü AbstractUser'da zaten var ve REQUIRED_FIELDS'da belirtildi.
    # Eğer username'in opsiyonel olmasını istiyorsanız, AbstractUser'daki username'i null=True, blank=True yapmanız veya
    # CustomUser'da username alanını null=True, blank=True olarak yeniden tanımlamanız gerekir.
    # Şu anki REQUIRED_FIELDS = ['username', 'first_name', 'last_name'] ayarınızda username zorunlu.

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

    objects = CustomUserManager() # Özel Manager'ı atadık

    USERNAME_FIELD = 'email' # Giriş için ana alan email
    # REQUIRED_FIELDS liste olarak USERNAME_FIELD dışındaki gerekli alanları belirtir.
    # phone alanının benzersizliği (unique) modeli kontrol etmelisiniz, şu an modelde unique değil.
    # Eğer username'in zorunlu olmasını istemiyorsanız, bunu REQUIRED_FIELDS'tan çıkarmanız
    # ve modeldeki username alanını null=True, blank=True yapmanız gerekir.
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        ordering = ['-date_joined']

    def __str__(self):
        if self.email and self.phone:
            return f"{self.get_full_name()} ({self.email} / {self.phone})"
        elif self.email:
            return f"{self.get_full_name()} ({self.email})"
        elif self.phone:
            return f"{self.get_full_name()} ({self.phone})"
        return self.username if self.username else "No Identifier"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def get_avatar_initial(self):
        """Avatar için baş harf"""
        if self.first_name:
            return self.first_name[0].upper()
        if self.email:
            return self.email[0].upper()
        return '?' # Email veya isim yoksa varsayılan bir harf

    def is_premium_user(self):
        """Premium kullanıcı kontrolü"""
        return self.current_plan in ['premium', 'enterprise']

    def days_until_plan_expires(self):
        """Plan bitimine kalan gün"""
        if self.plan_end_date:
            days = (self.plan_end_date - timezone.now()).days
            return max(0, days)
        return None


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
    