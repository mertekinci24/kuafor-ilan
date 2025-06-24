from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.jobs.models import JobListing, JobApplication, SavedJob
from apps.authentication.models import JobSeekerProfile, BusinessProfile
import json

User = get_user_model()


@login_required
def profile_view(request, user_id=None):
    """Profil görüntüleme - kendi profili veya başka kullanıcı profili"""
    
    if user_id:
        # Başka kullanıcının profili
        profile_user = get_object_or_404(User, id=user_id)
        is_own_profile = False
    else:
        # Kendi profili
        profile_user = request.user
        is_own_profile = True
    
    # Profil tipine göre veri hazırla
    profile_data = None
    user_stats = {
        'total_views': profile_user.profile_views,
        'join_date': profile_user.date_joined,
        'is_verified': getattr(profile_user, 'is_verified', False),
        'last_active': profile_user.last_login,
    }
    
    if profile_user.user_type == 'jobseeker':
        try:
            jobseeker_profile = profile_user.jobseeker_profile
            skills_text = getattr(jobseeker_profile, 'skills', '')
            skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()] if skills_text else []
            
            profile_data = {
                'type': 'jobseeker',
                'full_name': getattr(jobseeker_profile, 'full_name', profile_user.get_full_name()),
                'bio': getattr(jobseeker_profile, 'bio', ''),
                'city': getattr(jobseeker_profile, 'city', ''),
                'district': getattr(jobseeker_profile, 'district', ''),
                'experience_years': getattr(jobseeker_profile, 'experience_years', 0),
                'skills': getattr(jobseeker_profile, 'skills', ''),
                'skills_list': skills_list,
                'is_available': getattr(jobseeker_profile, 'is_available', True),
                'portfolio_images': getattr(jobseeker_profile, 'portfolio_images', ''),
            }
            
            if is_own_profile:
                user_stats.update({
                    'total_applications': getattr(jobseeker_profile, 'total_applications', 0),
                    'successful_applications': getattr(jobseeker_profile, 'successful_applications', 0),
                })
                
        except:
            # Profil yoksa boş profil oluştur
            profile_data = {
                'type': 'jobseeker',
                'full_name': profile_user.get_full_name(),
                'bio': '',
                'city': '',
                'district': '',
                'experience_years': 0,
                'skills': '',
                'skills_list': [],
                'is_available': True,
                'portfolio_images': '',
            }
    
    elif profile_user.user_type == 'business':
        try:
            business_profile = profile_user.business_profile
            profile_data = {
                'type': 'business',
                'business_name': getattr(business_profile, 'business_name', ''),
                'description': getattr(business_profile, 'description', ''),
                'city': getattr(business_profile, 'city', ''),
                'district': getattr(business_profile, 'district', ''),
                'address': getattr(business_profile, 'address', ''),
                'phone': getattr(business_profile, 'phone', ''),
                'website': getattr(business_profile, 'website', ''),
                'contact_person': getattr(business_profile, 'contact_person', ''),
                'is_verified': getattr(business_profile, 'is_verified', False),
            }
            
            if is_own_profile:
                user_stats.update({
                    'total_job_posts': getattr(business_profile, 'total_job_posts', 0),
                    'active_job_posts': getattr(business_profile, 'active_job_posts', 0),
                    'total_applications_received': getattr(business_profile, 'total_applications_received', 0),
                })
                
        except:
            # Profil yoksa boş profil oluştur
            profile_data = {
                'type': 'business',
                'business_name': '',
                'description': '',
                'city': '',
                'district': '',
                'address': '',
                'phone': '',
                'website': '',
                'contact_person': '',
                'is_verified': False,
            }
    
    # Eğer kendi profili ise son aktiviteleri getir
    recent_activities = []
    if is_own_profile:
        if profile_user.user_type == 'jobseeker':
            # Son başvurular
            applications = JobApplication.objects.filter(
                applicant=profile_user
            ).select_related('job')[:5]
            
            for app in applications:
                recent_activities.append({
                    'type': 'application',
                    'title': f"{app.job.title} pozisyonuna başvuru",
                    'company': app.job.business.get_full_name(),
                    'date': app.created_at,
                    'status': app.status
                })
        
        elif profile_user.user_type == 'business':
            # Son ilanlar
            jobs = JobListing.objects.filter(
                business=profile_user
            )[:5]
            
            for job in jobs:
                recent_activities.append({
                    'type': 'job_post',
                    'title': f"{job.title} ilanı",
                    'location': f"{job.city}, {job.district}",
                    'date': job.created_at,
                    'status': job.status
                })
    
    context = {
        'profile_user': profile_user,
        'profile_data': profile_data,
        'user_stats': user_stats,
        'is_own_profile': is_own_profile,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'profiles/profile.html', context)


@login_required
def profile_edit_view(request):
    """Profil düzenleme"""
    user = request.user
    
    if request.method == 'POST':
        try:
            # Temel kullanıcı bilgileri güncelle
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.save()
            
            if user.user_type == 'jobseeker':
                # İş arayan profili güncelle
                profile, created = JobSeekerProfile.objects.get_or_create(user=user)
                profile.full_name = request.POST.get('full_name', user.get_full_name())
                profile.bio = request.POST.get('bio', '')
                profile.city = request.POST.get('city', '')
                profile.district = request.POST.get('district', '')
                profile.experience_years = int(request.POST.get('experience_years', 0))
                profile.skills = request.POST.get('skills', '')
                profile.is_available = request.POST.get('is_available') == 'on'
                profile.save()
                
            elif user.user_type == 'business':
                # İş veren profili güncelle
                profile, created = BusinessProfile.objects.get_or_create(user=user)
                profile.business_name = request.POST.get('business_name', '')
                profile.description = request.POST.get('description', '')
                profile.city = request.POST.get('city', '')
                profile.district = request.POST.get('district', '')
                profile.address = request.POST.get('address', '')
                profile.phone = request.POST.get('phone', '')
                profile.website = request.POST.get('website', '')
                profile.contact_person = request.POST.get('contact_person', '')
                profile.save()
            
            messages.success(request, 'Profiliniz başarıyla güncellendi!')
            return redirect('profiles:profile')
            
        except Exception as e:
            messages.error(request, f'Profil güncellenirken hata oluştu: {str(e)}')
    
    # GET request - form verilerini hazırla
    profile_data = {}
    
    if user.user_type == 'jobseeker':
        try:
            profile = user.jobseeker_profile
            profile_data = {
                'full_name': profile.full_name,
                'bio': profile.bio,
                'city': profile.city,
                'district': profile.district,
                'experience_years': profile.experience_years,
                'skills': profile.skills,
                'is_available': profile.is_available,
            }
        except:
            profile_data = {
                'full_name': user.get_full_name(),
                'bio': '',
                'city': '',
                'district': '',
                'experience_years': 0,
                'skills': '',
                'is_available': True,
            }
    
    elif user.user_type == 'business':
        try:
            profile = user.business_profile
            profile_data = {
                'business_name': profile.business_name,
                'description': profile.description,
                'city': profile.city,
                'district': profile.district,
                'address': profile.address,
                'phone': profile.phone,
                'website': profile.website,
                'contact_person': profile.contact_person,
            }
        except:
            profile_data = {
                'business_name': '',
                'description': '',
                'city': '',
                'district': '',
                'address': '',
                'phone': '',
                'website': '',
                'contact_person': '',
            }
    
    context = {
        'user': user,
        'profile_data': profile_data,
    }
    
    return render(request, 'profiles/edit.html', context)


@login_required
def my_applications_view(request):
    """Başvurularım sayfası - sadece iş arayanlar"""
    if request.user.user_type != 'jobseeker':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('profiles:profile')
    
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__business').order_by('-created_at')
    
    context = {
        'applications': applications,
    }
    
    return render(request, 'profiles/applications.html', context)


@login_required
def saved_jobs_view(request):
    """Kayıtlı ilanlar sayfası - sadece iş arayanlar"""
    if request.user.user_type != 'jobseeker':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('profiles:profile')
    
    saved_jobs = SavedJob.objects.filter(
        user=request.user
    ).select_related('job', 'job__business').order_by('-created_at')
    
    context = {
        'saved_jobs': saved_jobs,
    }
    
    return render(request, 'profiles/saved_jobs.html', context)


@login_required
def my_jobs_view(request):
    """İlanlarım sayfası - sadece iş verenler"""
    if request.user.user_type != 'business':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('profiles:profile')
    
    jobs = JobListing.objects.filter(
        business=request.user
    ).order_by('-created_at')
    
    context = {
        'jobs': jobs,
    }
    
    return render(request, 'profiles/my_jobs.html', context)


@login_required
def settings_view(request):
    """Ayarlar sayfası"""
    if request.method == 'POST':
        try:
            user = request.user
            user.email_notifications = request.POST.get('email_notifications') == 'on'
            user.sms_notifications = request.POST.get('sms_notifications') == 'on'
            user.marketing_emails = request.POST.get('marketing_emails') == 'on'
            user.save()
            
            messages.success(request, 'Ayarlarınız başarıyla güncellendi!')
            
        except Exception as e:
            messages.error(request, f'Ayarlar güncellenirken hata oluştu: {str(e)}')
    
    return render(request, 'profiles/settings.html')


@login_required
def delete_account_view(request):
    """Hesap silme sayfası"""
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_delete')
        
        if confirm != 'HESABIMI SIL':
            messages.error(request, 'Onay metni yanlış yazıldı.')
            return render(request, 'profiles/delete_account.html')
        
        if not request.user.check_password(password):
            messages.error(request, 'Şifre yanlış.')
            return render(request, 'profiles/delete_account.html')
        
        # Hesabı sil
        request.user.delete()
        messages.success(request, 'Hesabınız başarıyla silindi.')
        return redirect('home')
    
    return render(request, 'profiles/delete_account.html')


# API Views
@login_required
@require_http_methods(["POST"])
def save_job_api(request):
    """İş ilanı kaydetme/kaldırma API"""
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        
        if not job_id:
            return JsonResponse({'success': False, 'message': 'İş ilanı ID gerekli'})
        
        job = get_object_or_404(JobListing, id=job_id)
        saved_job, created = SavedJob.objects.get_or_create(
            user=request.user,
            job=job
        )
        
        if not created:
            # Zaten kayıtlı, kaldır
            saved_job.delete()
            return JsonResponse({
                'success': True,
                'action': 'removed',
                'message': 'İlan kaydedilenlerden kaldırıldı'
            })
        else:
            # Yeni kayıt
            return JsonResponse({
                'success': True,
                'action': 'saved',
                'message': 'İlan başarıyla kaydedildi'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Hata oluştu: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def upload_avatar_api(request):
    """Avatar yükleme API - gelecekte kullanılmak üzere"""
    return JsonResponse({
        'success': False,
        'message': 'Avatar yükleme özelliği yakında eklenecek'
    })


@login_required
def export_profile_data(request):
    """Profil verilerini export etme - gelecekte kullanılmak üzere"""
    return JsonResponse({
        'success': False,
        'message': 'Veri export özelliği yakında eklenecek'
    })
    
