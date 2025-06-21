from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'user_type', 'is_email_verified', 'date_joined')
    list_filter = ('user_type', 'is_email_verified', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Ek Bilgiler', {'fields': ('user_type', 'phone', 'is_phone_verified', 'is_email_verified')}),
    )
  
