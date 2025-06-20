import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuafor_ilan.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@kuaforilan.com', 
        password='KuaforAdmin123!'
    )
    print("Admin user created successfully!")
else:
    print("Admin user already exists!")
  
