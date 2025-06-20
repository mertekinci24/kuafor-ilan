from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    list_display = [
        'email', 'username', 'full_name', 'user_type', 
        'is_email_verified', 'is_active', 'date_joined'
    ]
    list_filter = [
        'user_type', 'is_email_verified', 'is_active', 'date_joined'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': (
                'phone_number', 'user_type', 'avatar', 
                'is_email_verified', 'is_profile_complete', 'last_active'
            )
        }),
    )
  
