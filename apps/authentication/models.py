from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import TimeStampedModel

class CustomUser(AbstractUser, TimeStampedModel):
    """Custom user model for JobSeekers and Business owners"""
    USER_TYPES = (
        ('jobseeker', 'İş Arayan'),
        ('business', 'İş Veren'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
      
