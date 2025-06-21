from django.contrib import admin
from .models import JobCategory, JobListing, JobApplication

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'business', 'city', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'city', 'is_urgent')
    search_fields = ('title', 'business__email')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('applicant__email', 'job__title')
  
