from django.apps import AppConfig
from django.conf import settings


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    label = 'authentication'
    verbose_name = 'Authentication'
    
    def ready(self):
        # if not settings.DEBUG: # Admin oluşturma işlemi geçici olarak kapatıldı
        #    self.create_admin_user()
        pass # Boş bırakmamak için pass ekleyebiliriz
    
    def create_admin_user(self):
        """Admin kullanıcıyı otomatik oluştur"""
        try:
            from django.contrib.auth import get_user_model
            from apps.profiles.models import BusinessProfile
            
            User = get_user_model()
            
            # Admin kullanıcı kontrolü
            admin_user = User.objects.filter(email='admin@kuaforilan.com').first()
            
            if not admin_user:
                # Admin kullanıcı oluştur
                admin_user = User.objects.create_user(
                    username='admin',
                    email='admin@kuaforilan.com',
                    password='admin123',
                    first_name='Admin',
                    last_name='User',
                    user_type='business',
                    is_staff=True,
                    is_superuser=True,
                    is_verified=True,
                    email_verified=True,
                    phone_verified=True
                )

                # Business profil oluştur
                BusinessProfile.objects.get_or_create(
                    user=admin_user,
                    defaults={
                        'company_name': 'Kuaför İlan Admin',
                        'city': 'İstanbul',
                        'district': 'Beşiktaş',
                        'company_description': 'Platform yönetimi',
                        'contact_person': 'Admin User',
                        'contact_phone': '+90 555 000 00 00',
                        'is_verified': True
                    }
                )
                
                print("✅ Admin kullanıcı otomatik oluşturuldu!")
                print("📧 Email: admin@kuaforilan.com")
                print("🔑 Şifre: admin123")
            else:
                # Mevcut admin'in yetkilerini güncelle
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.is_verified = True
                admin_user.save()
                print("✅ Admin kullanıcı güncellendi!")
                
        except Exception as e:
            print(f"⚠️ Admin oluşturma hatası: {e}")
            
