from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import CustomUser # CustomUser, kendi uygulamasındaki models.py'den
from apps.profiles.models import JobSeekerProfile, BusinessProfile # Profil modelleri 'profiles' uygulamasından

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Kullanıcı oluşturulduğunda otomatik profil oluştur"""
    if created:
        if instance.user_type == 'jobseeker':
            # JobSeeker profili oluştur
            JobSeekerProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'city': '',
                    'experience_years': 0,  # ← INTEGER DEĞERİ
                    'skills': '',  # ← BOŞ STRING
                    'bio': '',
                }
            )
        elif instance.user_type == 'business':
            # Business profili oluştur
            BusinessProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'company_name': f"{instance.get_full_name()} Şirketi",
                    'company_size': '1-10',  # ← GEÇERLİ CHOICE
                    'establishment_year': timezone.now().year,
                    'city': '',
                    'address': '',
                    'contact_person': instance.get_full_name(),
                    'contact_phone': instance.phone or '',
                }
            )


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Kullanıcı kaydedildiğinde profili de kaydet"""
    try:
        if instance.user_type == 'jobseeker' and hasattr(instance, 'jobseeker_profile'):
            instance.jobseeker_profile.save()
        elif instance.user_type == 'business' and hasattr(instance, 'business_profile'):
            instance.business_profile.save()
    except:
        # Profil yoksa hata verme
        pass
    