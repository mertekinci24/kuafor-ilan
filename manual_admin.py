# Bu dosyayı railway.json ile çalıştıracağız
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuafor_ilan.settings')
django.setup()

from django.contrib.auth.models import User
admin_user = User.objects.create_superuser('admin', 'admin@kuaforilan.com', 'admin123')
print(f"Admin created: {admin_user.username}")
