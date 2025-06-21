import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuafor_ilan.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()  # CustomUser'ı kullanacak

# Eski admin'leri temizle
User.objects.filter(email='admin@kuaforilan.com').delete()

# Yeni CustomUser admin oluştur
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@kuaforilan.com', 
    password='admin123',
    user_type='business'  # CustomUser field'ı
)
print(f"CustomUser admin created: {admin_user.email}")
