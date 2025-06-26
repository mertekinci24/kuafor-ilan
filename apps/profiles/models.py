from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class JobSeekerProfile(TimeStampedModel):
    """Profile for job seekers (kuaförler)"""
    
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
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobseeker_profile')
    
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
    """Profile for business owners (salon sahipleri)"""
    
    COMPANY_SIZE_CHOICES = (
        ('1-10', '1-10 çalışan'),
        ('11-50', '11-50 çalışan'),
        ('51-200', '51-200 çalışan'),
        ('201-500', '201-500 çalışan'),
        ('500+', '500+ çalışan'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_profile')
    
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
        
