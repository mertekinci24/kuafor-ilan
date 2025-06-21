import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # core yerine proje adınızı yazın
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Environment variables'dan bilgileri al
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'KuaforAdmin123')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@kuaforilan.com')

# Superuser oluştur (yoksa)
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists!")
  
