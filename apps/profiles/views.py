from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import logging

from .models import JobSeekerProfile, BusinessProfile
from apps.jobs.models import JobApplication, JobListing, SavedJob

User = get_user_model()
logger = logging.getLogger(__name__)


@login_required
def profile_view(request, user_id=None):
    """Profil görüntüleme sayfası"""
    
    # Eğer user_id verilmemişse, kendi profilini göster
    if user_id is None:
        user = request.user
    else:
        user = get_object_or_404(User, id=user_id)
        # Profil görüntülenme sayısını artır (başkasının profilini görürse)
        if user != request.user:
            user.profile_views += 1
            user.save()
    
    # Profil tipine göre profil verisini al
    profile = None
    profile_type = user.user_type
    
    if profile_type == 'jobseeker':
        try:
            profile = user.jobseeker_profile
        except:
            # Profil yoksa oluştur
            profile = JobSeekerProfile.objects.create(
                user=user,
                city="İstanbul"  # Varsayılan
            )
    
    elif profile_type == 'business':
        try:
            profile = user.business_profile
        except:
            # Profil yoksa oluştur
            profile = BusinessProfile.objects.create(
                user=user,
                company_name=f"{user.first_name} {user.last_name}",
                city="İstanbul",
                contact_phone=user.phone or "",
                address="Belirtilmemiş"
            )
    
    # İstatistikler
    stats = {}
    recent_activities = []
    
    if profile_type == 'jobseeker':
        # İş arayan istatistikleri
        applications = JobApplication.objects.filter(applicant=user)
        saved_jobs = SavedJob.objects.filter(user=user)
        
        stats = {
            'total_applications': applications.count(),
            'pending_applications': applications.filter(status='pending').count(),
            'accepted_applications': applications.filter(status='accepted').count(),
            'rejected_applications': applications.filter(status='rejected').count(),
            'saved_jobs': saved_jobs.count(),
            'profile_views': user.profile_views,
        }
        
        # Son başvurular
        recent_activities = applications.order_by('-created_at')[:5]
        
    elif profile_type == 'business':
        # İş veren istatistikleri
        job_listings = JobListing.objects.filter(business=user)
        all_applications = JobApplication.objects.filter(job__business=user)
        
        stats = {
            'total_jobs': job_listings.count(),
            'active_jobs': job_listings.filter(status='active').count(),
            'closed_jobs': job_listings.filter(status='closed').count(),
            'total_applications': all_applications.count(),
            'pending_applications': all_applications.filter(status='pending').count(),
            'profile_views': user.profile_views,
        }
        
        # Son ilanlar
        recent_activities = job_listings.order_by('-created_at')[:5]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'profile_type': profile_type,
        'stats': stats,
        'recent_activities': recent_activities,
        'is_own_profile': user == request.user,
    }
    
    return render(request, 'profiles/profile.html', context)


@login_required
def profile_edit_view(request):
    """Profil düzenleme sayfası"""
    
    # Kullanıcının profil tipine göre profil objesini al veya oluştur
    profile = None
    profile_type = request.user.user_type
    
    if profile_type == 'jobseeker':
        profile, created = JobSeekerProfile.objects.get_or_create(
            user=request.user,
            defaults={'city': 'İstanbul'}
        )
    elif profile_type == 'business':
        profile, created = BusinessProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'company_name': f"{request.user.first_name} {request.user.last_name}",
                'city': 'İstanbul',
                'contact_phone': request.user.phone or "",
                'address': 'Belirtilmemiş'
            }
        )
    
    if request.method == 'POST':
        try:
            # Temel kullanıcı bilgileri güncelleme
            request.user.first_name = request.POST.get('first_name', '').strip()
            request.user.last_name = request.POST.get('last_name', '').strip()
            
            # Email güncellemesi (benzersizlik kontrolü)
            new_email = request.POST.get('email', '').strip()
            if new_email != request.user.email:
                if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                    messages.error(request, 'Bu e-posta adresi zaten kullanımda.')
                    return render(request, 'profiles/profile_edit.html', {
                        'profile': profile,
                        'profile_type': profile_type,
                    })
                request.user.email = new_email
                request.user.email_verified = False  # Yeni email doğrulanmalı
            
            request.user.phone = request.POST.get('phone', '').strip()
            request.user.save()
            
            # Profil tipine göre özel alanları güncelle
            if profile_type == 'jobseeker':
                profile.bio = request.POST.get('bio', '').strip()
                profile.experience_years = int(request.POST.get('experience_years', 0) or 0)
                profile.skills = request.POST.get('skills', '').strip()
                profile.city = request.POST.get('city', '').strip()
                profile.district = request.POST.get('district', '').strip()
                profile.address = request.POST.get('address', '').strip()
                profile.portfolio_url = request.POST.get('portfolio_url', '').strip()
                profile.linkedin_url = request.POST.get('linkedin_url', '').strip()
                profile.is_available = request.POST.get('is_available') == 'on'
                
                # Maaş beklentisi
                expected_salary_min = request.POST.get('expected_salary_min', '').strip()
                expected_salary_max = request.POST.get('expected_salary_max', '').strip()
                profile.expected_salary_min = int(expected_salary_min) if expected_salary_min else None
                profile.expected_salary_max = int(expected_salary_max) if expected_salary_max else None
                
            elif profile_type == 'business':
                profile.company_name = request.POST.get('company_name', '').strip()
                profile.company_description = request.POST.get('company_description', '').strip()
                profile.company_size = request.POST.get('company_size', '')
                profile.establishment_year = request.POST.get('establishment_year', '')
                profile.establishment_year = int(profile.establishment_year) if profile.establishment_year else None
                
                profile.city = request.POST.get('city', '').strip()
                profile.district = request.POST.get('district', '').strip()
                profile.address = request.POST.get('address', '').strip()
                profile.website = request.POST.get('website', '').strip()
                
                profile.contact_person = request.POST.get('contact_person', '').strip()
                profile.contact_phone = request.POST.get('contact_phone', '').strip()
            
            # Dosya yüklemeleri
            if 'profile_image' in request.FILES:
                profile.profile_image = request.FILES['profile_image']
            
            if 'cv_file' in request.FILES and profile_type == 'jobseeker':
                profile.cv_file = request.FILES['cv_file']
            
            if 'logo' in request.FILES and profile_type == 'business':
                profile.logo = request.FILES['logo']
            
            profile.save()
            
            messages.success(request, 'Profiliniz başarıyla güncellendi!')
            logger.info(f"Profile updated: {request.user.email}")
            return redirect('profiles:profile')
            
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            messages.error(request, f'Profil güncellenirken hata oluştu: {str(e)}')
    
    context = {
        'profile': profile,
        'profile_type': profile_type,
        'user': request.user,
    }
    
    return render(request, 'profiles/profile_edit.html', context)


@login_required
def my_applications_view(request):
    """Kullanıcının başvurularını listele (sadece job seeker için)"""
    
    if request.user.user_type != 'jobseeker':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('profiles:profile')
    
    # Filtreleme
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    applications = JobApplication.objects.filter(applicant=request.user)
    
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    if search_query:
        applications = applications.filter(
            Q(job__title__icontains=search_query) |
            Q(job__business__first_name__icontains=search_query) |
            Q(job__business__last_name__icontains=search_query)
        )
    
    applications = applications.order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': JobApplication.STATUS_CHOICES,
    }
    
    return render(request, 'profiles/my_applications.html', context)


@login_required
def my_jobs_view(request):
    """İş verenin ilanlarını listele (sadece business için)"""
    
    if request.user.user_type != 'business':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('profiles:profile')
    
    # Filtreleme
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    jobs = JobListing.objects.filter(business=request.user)
    
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)
    
    jobs = jobs.order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': JobListing.STATUS_CHOICES,
    }
    
    return render(request, 'profiles/my_jobs.html', context)


@login_required
def saved_jobs_view(request):
    """Kaydedilen iş ilanları"""
    
    if request.user.user_type != 'jobseeker':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('profiles:profile')
    
    saved_jobs = SavedJob.objects.filter(user=request.user).order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(saved_jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'profiles/saved_jobs.html', context)


@login_required
@require_http_methods(["POST"])
def save_job_api(request):
    """İş ilanını kaydet/kaldır API"""
    
    if request.user.user_type != 'jobseeker':
        return JsonResponse({
            'success': False,
            'message': 'Bu işlem sadece iş arayanlar için geçerlidir.'
        })
    
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        
        job = get_object_or_404(JobListing, id=job_id, status='active')
        
        saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
        
        if created:
            return JsonResponse({
                'success': True,
                'saved': True,
                'message': 'İlan kaydedildi!'
            })
        else:
            saved_job.delete()
            return JsonResponse({
                'success': True,
                'saved': False,
                'message': 'İlan kaydetme kaldırıldı!'
            })
            
    except Exception as e:
        logger.error(f"Save job API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Bir hata oluştu.'
        })


@login_required
@require_http_methods(["POST"])
def upload_avatar_api(request):
    """Avatar yükleme API"""
    
    try:
        if 'avatar' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': 'Dosya seçilmedi.'
            })
        
        avatar_file = request.FILES['avatar']
        
        # Dosya boyutu kontrolü (5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'message': 'Dosya boyutu 5MB\'dan küçük olmalıdır.'
            })
        
        # Dosya tipı kontrolü
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'message': 'Sadece resim dosyaları yüklenebilir.'
            })
        
        # Profili al veya oluştur
        if request.user.user_type == 'jobseeker':
            profile, created = JobSeekerProfile.objects.get_or_create(
                user=request.user,
                defaults={'city': 'İstanbul'}
            )
            profile.profile_image = avatar_file
        elif request.user.user_type == 'business':
            profile, created = BusinessProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'company_name': f"{request.user.first_name} {request.user.last_name}",
                    'city': 'İstanbul',
                    'contact_phone': request.user.phone or "",
                    'address': 'Belirtilmemiş'
                }
            )
            profile.logo = avatar_file
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profil fotoğrafı güncellendi!',
            'avatar_url': profile.profile_image.url if hasattr(profile, 'profile_image') and profile.profile_image else None
        })
        
    except Exception as e:
        logger.error(f"Avatar upload error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Dosya yüklenirken hata oluştu.'
        })


@login_required
def settings_view(request):
    """Kullanıcı ayarları"""
    
    if request.method == 'POST':
        try:
            # Bildirim ayarları
            request.user.email_notifications = request.POST.get('email_notifications') == 'on'
            request.user.sms_notifications = request.POST.get('sms_notifications') == 'on'
            request.user.marketing_emails = request.POST.get('marketing_emails') == 'on'
            
            request.user.save()
            
            messages.success(request, 'Ayarlarınız kaydedildi!')
            
        except Exception as e:
            logger.error(f"Settings update error: {str(e)}")
            messages.error(request, 'Ayarlar kaydedilirken hata oluştu.')
    
    return render(request, 'profiles/settings.html')


@login_required
def delete_account_view(request):
    """Hesap silme"""
    
    if request.method == 'POST':
        password = request.POST.get('password')
        
        if request.user.check_password(password):
            # Hesabı soft delete (is_active = False)
            request.user.is_active = False
            request.user.save()
            
            messages.success(request, 'Hesabınız başarıyla kapatıldı.')
            logger.info(f"Account deactivated: {request.user.email}")
            
            from django.contrib.auth import logout
            logout(request)
            return redirect('home')
        else:
            messages.error(request, 'Şifre hatalı.')
    
    return render(request, 'profiles/delete_account.html')


@login_required
def export_profile_data(request):
    """Profil verilerini export et (GDPR uyumluluğu için)"""
    
    try:
        profile_data = {
            'user_info': {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': request.user.phone,
                'user_type': request.user.user_type,
                'date_joined': request.user.date_joined.isoformat(),
                'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
            },
            'export_date': timezone.now().isoformat(),
        }
        
        # Profil bilgilerini ekle
        if request.user.user_type == 'jobseeker' and hasattr(request.user, 'jobseeker_profile'):
            profile = request.user.jobseeker_profile
            profile_data['jobseeker_profile'] = {
                'bio': profile.bio,
                'city': profile.city,
                'district': profile.district,
                'experience_years': profile.experience_years,
                'skills': profile.skills,
                'is_available': profile.is_available,
            }
        elif request.user.user_type == 'business' and hasattr(request.user, 'business_profile'):
            profile = request.user.business_profile
            profile_data['business_profile'] = {
                'company_name': profile.company_name,
                'company_description': profile.company_description,
                'city': profile.city,
                'district': profile.district,
                'address': profile.address,
                'website': profile.website,
            }
        
        response = JsonResponse(profile_data, json_dumps_params={'indent': 2})
        response['Content-Disposition'] = f'attachment; filename="profile_data_{request.user.id}.json"'
        
        return response
        
    except Exception as e:
        logger.error(f"Export profile data error: {str(e)}")
        messages.error(request, 'Veri export edilirken hata oluştu.')
        return redirect('profiles:settings')
        
