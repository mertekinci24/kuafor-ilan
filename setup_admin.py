import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuafor_ilan.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Environment variables'dan bilgileri al
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'KuaforAdmin123')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@kuaforilan.com')

# Mevcut admin user'ı kontrol et
try:
    user = User.objects.get(username=username)
    user.set_password(password)  # Şifreyi güncelle
    user.email = email
    user.save()
    print(f"Superuser '{username}' password updated!")
except User.DoesNotExist:
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully!")
    
