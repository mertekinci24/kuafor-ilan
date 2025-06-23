from django.contrib import admin
from .models import JobCategory, JobListing, JobApplication, SavedJob, JobView


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(JobListing)  
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'business', 'city', 'status', 'views_count', 'created_at')
    list_filter = ('status', 'city', 'category', 'is_urgent', 'created_at')
    search_fields = ('title', 'business__email', 'city', 'description')
    readonly_fields = ('views_count', 'created_at', 'updated_at')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('applicant__email', 'job__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    search_fields = ('user__email', 'job__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(JobView)
class JobViewAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('job__title', 'user__email', 'ip_address')
    readonly_fields = ('created_at', 'updated_at')
    
