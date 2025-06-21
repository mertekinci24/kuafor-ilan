from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

class JobSeekerProfile(TimeStampedModel):
    """Profile for job seekers (kuaförler)"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    skills = models.TextField(blank=True, help_text="Yetenekler virgül ile ayrılsın")
    portfolio_images = models.TextField(blank=True, help_text="Fotoğraf URL'leri")
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, blank=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.city}"

class BusinessProfile(TimeStampedModel):
    """Profile for business owners (salon sahipleri)"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=15)
    website = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.business_name} - {self.city}"
      
