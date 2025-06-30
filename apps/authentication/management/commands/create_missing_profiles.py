# apps/authentication/management/commands/create_missing_profiles.py

from django.core.management.base import BaseCommand
from apps.authentication.models import CustomUser
from apps.profiles.models import JobSeekerProfile, BusinessProfile
import sys 

class Command(BaseCommand):
    help = 'Veritabanındaki mevcut kullanıcılar için eksik profilleri oluşturur.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Mevcut kullanıcılar için profiller kontrol ediliyor ve oluşturuluyor..."))

        for user in CustomUser.objects.all():
            if not hasattr(user, 'jobseeker_profile') and not hasattr(user, 'business_profile'):
                self.stdout.write(f"Kullanıcı {user.username} için profil bulunamadı, oluşturuluyor...")
                if user.user_type == 'jobseeker':
                    profile, created = JobSeekerProfile.objects.get_or_create(user=user)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✅ JobSeekerProfile oluşturuldu: {user.username}"))
                    else:
                        self.stdout.write(f"🔄 JobSeekerProfile zaten vardı (get_or_create): {user.username}")
                elif user.user_type == 'business':
                    profile, created = BusinessProfile.objects.get_or_create(user=user)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✅ BusinessProfile oluşturuldu: {user.username}"))
                    else:
                        self.stdout.write(f"🔄 BusinessProfile zaten vardı (get_or_create): {user.username}")
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Kullanıcı {user.username} için bilinmeyen user_type: {user.user_type}. Profil oluşturulmadı."))
            else:
                self.stdout.write(f"Kullanıcı {user.username} zaten bir profile sahip.")

        self.stdout.write(self.style.SUCCESS("Profil oluşturma/kontrol işlemi tamamlandı."))