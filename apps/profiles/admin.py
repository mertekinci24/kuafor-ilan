from django.contrib import admin
from .models import JobSeekerProfile, BusinessProfile

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'city', 'experience_years', 'is_available')
    list_filter = ('city', 'is_available')

@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'city', 'phone')
    list_filter = ('city',)
  
