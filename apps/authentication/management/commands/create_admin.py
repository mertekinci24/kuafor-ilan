from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.authentication.models import BusinessProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Admin kullanıcı oluşturur (Email: admin@kuaforilan.com, Şifre: admin123)'

    def handle(self, *args, **options):
        self.stdout.write('👤 Admin kullanıcı kontrol ediliyor...')
        
        # Admin kullanıcı kontrolü
        admin_user = User.objects.filter(email='admin@kuaforilan.com').first()
        
        if admin_user:
            self.stdout.write(
                self.style.WARNING('⚠️ Admin kullanıcı zaten mevcut!')
            )
            # Şifreyi güncelle (emin olmak için)
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_verified = True
            admin_user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Admin kullanıcı şifresi güncellendi!\n'
                    '📧 Email: admin@kuaforilan.com\n'
                    '🔑 Şifre: admin123'
                )
            )
            return

        # Admin kullanıcı oluştur
        try:
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

            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Admin kullanıcı başarıyla oluşturuldu!\n\n'
                    '🔐 GİRİŞ BİLGİLERİ:\n'
                    '📧 Email: admin@kuaforilan.com\n'
                    '🔑 Şifre: admin123\n'
                    '👨‍💼 Rol: Admin + İş Veren\n\n'
                    '🌐 Giriş URL\'leri:\n'
                    '🏠 Ana Site: /auth/login/\n'
                    '⚙️ Admin Panel: /admin/\n'
                    '📊 Dashboard: /dashboard/'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Hata oluştu: {str(e)}')
            )
            
