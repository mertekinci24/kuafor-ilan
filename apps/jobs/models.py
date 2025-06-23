from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

class JobCategory(TimeStampedModel):
    """İş kategorileri (Kadın Kuaförü, Erkek Kuaförü, vs.)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Job Categories"

class JobListing(TimeStampedModel):
    """İş ilanları"""
    STATUS_CHOICES = (
        ('active', 'Aktif'),
        ('closed', 'Kapalı'),
        ('paused', 'Duraklatıldı'),
    )
    
    business = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    is_urgent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    views_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} - {self.city}"

class JobApplication(TimeStampedModel):
    """İş başvuruları"""
    STATUS_CHOICES = (
        ('pending', 'Beklemede'),
        ('reviewed', 'İncelendi'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
    )
    
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"{self.applicant.email} -> {self.job.title}"
    
    class Meta:
        unique_together = ('job', 'applicant')


class SavedJob(TimeStampedModel):
    """Kaydedilen iş ilanları"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.email} -> {self.job.title}"
    
    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-created_at']


class JobView(TimeStampedModel):
    """İş ilanı görüntülenme takibi"""
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    
    def __str__(self):
        return f"{self.job.title} - {self.ip_address}"
    
    class Meta:
        ordering = ['-created_at']
        
