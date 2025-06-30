from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import json
import logging

from .models import JobSeekerProfile, BusinessProfile
from apps.jobs.models import JobListing, JobApplication, SavedJob
from .forms import JobSeekerProfileForm, BusinessProfileForm

User = get_user_model()
logger = logging.getLogger(__name__)


@login_required
def profile_view(request, user_id=None):
    """Profil görüntüleme - kendi profili veya başka kullanıcı profili"""
    
    if user_id:
        # Başka kullanıcının profilini görüntüle
        try:
            user = get_object_or_404(User, id=user_id)
            is_own_profile = (user == request.user)
            
            # Profil görüntüleme sayısını artır (kendi profili değilse)
            if not is_own_profile:
                if hasattr(user, 'profile_views'):
                    user.profile_views += 1
                    user.save(update_fields=['profile_views'])
            
        except User.DoesNotExist:
            messages.error(request, 'Kullanıcı bulunamadı.')
            return redirect('/')
    else:
        # Kendi profilini görüntüle
        user = request.user
        is_own_profile = True
    
    # Profil tipine göre template ve context hazırla
    if hasattr(user, 'jobseeker_profile'):
        profile = user.jobseeker_profile
        template = 'profiles/profile.html'
        
        # İş arayan için ek bilgiler
        context = {
            'user': user,
            'profile': profile,
            'is_own_profile': is_own_profile,
            'skills_list': profile.get_skills_list() if hasattr(profile, 'get_skills_list') else (profile.skills.split(',') if hasattr(profile, 'skills') and profile.skills else []),
            'experience_text': profile.get_experience_display_text() if hasattr(profile, 'get_experience_display_text') else f"{getattr(profile, 'experience_years', 0)} yıl deneyim",
        }
        
        # Kendi profiliyse başvuru istatistikleri ekle
        if is_own_profile:
            context.update({
                'total_applications': getattr(profile, 'total_applications', 0),
            })
            
            # JobApplication modeliniz varsa bu satırları aktif edin:
            try:
                recent_applications = JobApplication.objects.filter(
                    applicant=user
                ).select_related('job')[:5]
                context['recent_applications'] = recent_applications
            except:
                context['recent_applications'] = []
            
    elif hasattr(user, 'business_profile'):
        profile = user.business_profile
        template = 'profiles/profile.html'
        
        # İş veren için ek bilgiler
        context = {
            'user': user,
            'profile': profile,
            'is_own_profile': is_own_profile,
        }
        
        # Kendi profiliyse iş ilanları ve başvurular ekle
        if is_own_profile:
            context.update({
                'total_job_posts': getattr(profile, 'total_job_posts', 0),
                'active_job_posts': getattr(profile, 'active_job_posts', 0),
            })
            
            # JobListing modeliniz varsa bu satırları aktif edin:
            try:
                recent_jobs = JobListing.objects.filter(
                    business=user
                ).order_by('-created_at')[:5]
                context['recent_jobs'] = recent_jobs
            except:
                context['recent_jobs'] = []
        else:
            # Başkasının profili - sadece aktif iş ilanlarını göster
            try:
                public_jobs = JobListing.objects.filter(
                    business=user,
                    status='active'
                ).order_by('-created_at')[:5]
                context['public_jobs'] = public_jobs
            except:
                context['public_jobs'] = []
    else:
        # Profil oluşturulmamış - varsayılan profil bilgileri
        template = 'profiles/profile.html'
        context = {
            'user': user,
            'profile': None,
            'is_own_profile': is_own_profile,
            'skills_list': [],
            'experience_text': 'Henüz profil oluşturulmamış',
        }

    # Template için profil verilerini hazırla (YENİ ÖZELLIKLER)
    profile_data = get_profile_data(user)
    user_stats = calculate_user_stats(user)
    profile_completion_percentage = calculate_profile_completion(user, profile_data)
    completion_items = get_completion_items(user, profile_data)
    recent_activities = get_recent_activities(user)
    
    # Context'e yeni template verileri ekle (MEVCUT ÖZELLIKLERE EK OLARAK)
    context.update({
        'profile_user': user,
        'profile_data': profile_data,
        'user_stats': user_stats,
        'profile_completion_percentage': profile_completion_percentage,
        'completion_items': completion_items,
        'recent_activities': recent_activities,
        'monthly_growth': "+12%",
    })
    
    return render(request, template, context)


@login_required
def profile_edit_view(request):
    """Profil düzenleme"""
    
    if hasattr(request.user, 'jobseeker_profile'):
        profile = request.user.jobseeker_profile
        form_class = JobSeekerProfileForm
        template = 'profiles/profile_edit.html'
        
    elif hasattr(request.user, 'business_profile'):
        profile = request.user.business_profile
        form_class = BusinessProfileForm
        template = 'profiles/profile_edit.html'
    else:
        messages.error(request, 'Profiliniz bulunamadı.')
        return redirect('/')
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Profiliniz başarıyla güncellendi.')
                logger.info(f"Profile updated: {request.user.email}")
                return redirect('profiles:profile')
                
            except Exception as e:
                logger.error(f"Profile update error for {request.user.email}: {str(e)}")
                messages.error(request, 'Profil güncellenirken hata oluştu.')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = form_class(instance=profile)
    
    # Template için profil verilerini hazırla
    profile_data = get_profile_data(request.user)
    user_stats = calculate_user_stats(request.user)
    profile_completion_percentage = calculate_profile_completion(request.user, profile_data)
    completion_items = get_completion_items(request.user, profile_data)
    recent_activities = get_recent_activities(request.user)
    
    context = {
        'form': form,
        'profile': profile,
        'user': request.user,
        'profile_user': request.user,
        'profile_data': profile_data,
        'user_stats': user_stats,
        'profile_completion_percentage': profile_completion_percentage,
        'completion_items': completion_items,
        'recent_activities': recent_activities,
        'is_own_profile': True,
        'monthly_growth': "+12%",
        'profile_type': 'jobseeker' if hasattr(request.user, 'jobseeker_profile') else 'business',
    }
    
    return render(request, template, context)


@login_required
def profile_completion_wizard_view(request):
    """Profil tamamlama sihirbazı"""
    
    # Kullanıcının profil tipini belirle
    if hasattr(request.user, 'jobseeker_profile'):
        profile = request.user.jobseeker_profile
        form_class = JobSeekerProfileForm
        profile_type = 'jobseeker'
        steps = {
            1: ['bio', 'experience_years', 'skills'],
            2: ['city', 'district', 'address'],
            3: ['birth_date', 'portfolio_url', 'linkedin_url', 'cv_file', 'profile_image', 'certificates', 'expected_salary_min', 'expected_salary_max', 'is_available'],
        }
        step_titles = {
            1: 'Kişisel Bilgiler',
            2: 'Konum Bilgileri',
            3: 'Detaylı Bilgiler ve Dosyalar',
        }
    elif hasattr(request.user, 'business_profile'):
        profile = request.user.business_profile
        form_class = BusinessProfileForm
        profile_type = 'business'
        steps = {
            1: ['company_name', 'company_description', 'company_size', 'establishment_year'],
            2: ['city', 'district', 'address', 'contact_phone', 'website', 'contact_person'],
            3: ['is_verified', 'verification_documents', 'logo', 'cover_image'],
        }
        step_titles = {
            1: 'Şirket Bilgileri',
            2: 'İletişim Bilgileri',
            3: 'Doğrulama ve Görseller',
        }
    else:
        messages.error(request, 'Profiliniz bulunamadı.')
        return redirect('/')

    current_step = int(request.POST.get('current_step', 1)) if request.method == 'POST' else 1
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        
        # Sadece mevcut adımdaki alanları doğrula
        form.fields = {k: v for k, v in form.fields.items() if k in steps[current_step]}
        
        if form.is_valid():
            # Form verilerini kaydet
            for field_name in steps[current_step]:
                if field_name in request.FILES:
                    setattr(profile, field_name, request.FILES[field_name])
                else:
                    setattr(profile, field_name, form.cleaned_data.get(field_name))
            profile.save()
            
            if current_step < len(steps):
                current_step += 1
                messages.success(request, 'Adım başarıyla tamamlandı!')
            else:
                messages.success(request, 'Profiliniz başarıyla tamamlandı!')
                return redirect('profiles:profile')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    
    # Mevcut adım için formu yeniden oluştur
    form = form_class(instance=profile)
    # Sadece mevcut adımdaki alanları göster
    form.fields = {k: v for k, v in form.fields.items() if k in steps[current_step]}

    context = {
        'form': form,
        'profile': profile,
        'user': request.user,
        'current_step': current_step,
        'total_steps': len(steps),
        'step_title': step_titles.get(current_step, 'Profil Tamamlama'),
        'profile_type': profile_type,
    }
    
    return render(request, 'profiles/profile_wizard.html', context)


@login_required
def my_applications_view(request):
    """Başvurularım (sadece iş arayanlar için)"""
    
    if not hasattr(request.user, 'jobseeker_profile'):
        messages.error(request, 'Bu sayfa sadece iş arayanlar için.')
        return redirect('/')
    
    # Başvuruları getir
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__business').order_by('-applied_at')
    
    # Filtreleme
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Sayfalama
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    applications_page = paginator.get_page(page_number)
    
    # İstatistikler
    stats = {
        'total': applications.count(),
        'pending': applications.filter(status='pending').count(),
        'reviewing': applications.filter(status='reviewing').count(),
        'interview': applications.filter(status='interview').count(),
        'hired': applications.filter(status='hired').count(),
        'rejected': applications.filter(status='rejected').count(),
    }
    
    context = {
        'applications': applications_page.object_list,
        'applications_page': applications_page,
        'stats': stats,
        'current_status_filter': status_filter,
        'status_choices': JobApplication._meta.get_field('status').choices,
    }
    
    return render(request, 'profiles/my_applications.html', context)


@login_required
def saved_jobs_view(request):
    """Kaydedilen işler (sadece iş arayanlar için)"""
    
    if not hasattr(request.user, 'jobseeker_profile'):
        messages.error(request, 'Bu sayfa sadece iş arayanlar için.')
        return redirect('/')
    
    # Kaydedilen işleri getir
    saved_jobs = SavedJob.objects.filter(
        user=request.user
    ).select_related('job', 'job__business', 'job__category').order_by('-saved_at')
    
    # Sayfalama
    paginator = Paginator(saved_jobs, 12)
    page_number = request.GET.get('page')
    saved_jobs_page = paginator.get_page(page_number)
    
    context = {
        'saved_jobs': saved_jobs_page.object_list,
        'saved_jobs_page': saved_jobs_page,
    }
    
    return render(request, 'profiles/saved_jobs.html', context)


@login_required
def my_jobs_view(request):
    """İlanlarım (sadece iş verenler için)"""
    
    if not hasattr(request.user, 'business_profile'):
        messages.error(request, 'Bu sayfa sadece iş verenler için.')
        return redirect('/')
    
    # İş ilanlarını getir
    jobs = JobListing.objects.filter(
        business=request.user
    ).select_related('category').order_by('-created_at')
    
    # Filtreleme
    status_filter = request.GET.get('status', '')
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    
    # Sayfalama
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    jobs_page = paginator.get_page(page_number)
    
    # İstatistikler
    stats = {
        'total': jobs.count(),
        'active': jobs.filter(status='active').count(),
        'draft': jobs.filter(status='draft').count(),
        'paused': jobs.filter(status='paused').count(),
        'closed': jobs.filter(status='closed').count(),
        'filled': jobs.filter(status='filled').count(),
    }
    
    context = {
        'jobs': jobs_page.object_list,
        'jobs_page': jobs_page,
        'stats': stats,
        'current_status_filter': status_filter,
        'status_choices': JobListing._meta.get_field('status').choices,
    }
    
    return render(request, 'profiles/my_jobs.html', context)


@login_required
def settings_view(request):
    """Profil ayarları"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_notifications':
            # Bildirim ayarları güncelle
            user = request.user
            user.email_notifications = request.POST.get('email_notifications') == 'on'
            user.sms_notifications = request.POST.get('sms_notifications') == 'on'
            user.marketing_emails = request.POST.get('marketing_emails') == 'on'
            user.save()
            
            messages.success(request, 'Bildirim ayarlarınız güncellendi.')
            
        elif action == 'change_password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not request.user.check_password(current_password):
                messages.error(request, 'Mevcut şifreniz hatalı.')
            elif new_password != confirm_password:
                messages.error(request, 'Yeni şifreler eşleşmiyor.')
            elif len(new_password) < 8:
                messages.error(request, 'Şifre en az 8 karakter olmalıdır.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Şifreniz başarıyla güncellendi.')
                
        elif action == 'update_privacy':
            # Gizlilik ayarları (ileride eklenebilir)
            messages.info(request, 'Gizlilik ayarları henüz aktif değil.')
        
        return redirect('profiles:settings')
    
    context = {
        'user': request.user,
    }
    
    return render(request, 'profiles/settings.html', context)


@login_required
def delete_account_view(request):
    """Hesap silme"""
    
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        password = request.POST.get('password')
        
        if confirmation != 'KALICI OLARAK SIL':
            messages.error(request, 'Onay metni hatalı.')
            return render(request, 'profiles/delete_account.html')
        
        if not request.user.check_password(password):
            messages.error(request, 'Şifreniz hatalı.')
            return render(request, 'profiles/delete_account.html')
        
        try:
            user_email = request.user.email
            request.user.delete()
            
            logger.info(f"User account deleted: {user_email}")
            messages.success(request, 'Hesabınız kalıcı olarak silindi.')
            
            return redirect('/')
            
        except Exception as e:
            logger.error(f"Account deletion error for {request.user.email}: {str(e)}")
            messages.error(request, 'Hesap silinirken hata oluştu.')
    
    return render(request, 'profiles/delete_account.html')


# API Views
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def save_job_api(request):
    """İş ilanı kaydetme/kaldırma API"""
    
    if not hasattr(request.user, 'jobseeker_profile'):
        return JsonResponse({
            'success': False,
            'message': 'Bu özellik sadece iş arayanlar için.'
        })
    
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        
        if not job_id:
            return JsonResponse({
                'success': False,
                'message': 'İş ilanı ID gerekli.'
            })
        
        job = get_object_or_404(JobListing, id=job_id, status='active')
        
        # Zaten kaydedilmiş mi kontrol et
        saved_job, created = SavedJob.objects.get_or_create(
            user=request.user,
            job=job
        )
        
        if created:
            message = 'İş ilanı kaydedildi.'
            action = 'saved'
        else:
            saved_job.delete()
            message = 'İş ilanı kayıtlı listeden çıkarıldı.'
            action = 'removed'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'action': action
        })
        
    except JobListing.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'İş ilanı bulunamadı.'
        })
    except Exception as e:
        logger.error(f"Save job API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'İşlem sırasında hata oluştu.'
        })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def upload_avatar_api(request):
    """Avatar yükleme API"""
    
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
            'message': 'Dosya boyutu 5MB\'dan büyük olamaz.'
        })
    
    # Dosya tipi kontrolü
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if avatar_file.content_type not in allowed_types:
        return JsonResponse({
            'success': False,
            'message': 'Sadece JPG, PNG, GIF ve WebP dosyaları yüklenebilir.'
        })
    
    try:
        # Profil tipine göre avatar kaydet
        if hasattr(request.user, 'jobseeker_profile'):
            profile = request.user.jobseeker_profile
            profile.profile_image = avatar_file
            profile.save()
        elif hasattr(request.user, 'business_profile'):
            profile = request.user.business_profile
            profile.logo = avatar_file
            profile.save()
        else:
            return JsonResponse({
                'success': False,
                'message': 'Profil bulunamadı.'
            })
        
        return JsonResponse({
            'success': True,
            'message': 'Avatar başarıyla güncellendi.',
            'avatar_url': profile.profile_image.url if hasattr(profile, 'profile_image') else profile.logo.url
        })
        
    except Exception as e:
        logger.error(f"Avatar upload error for {request.user.email}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Avatar yüklenirken hata oluştu.'
        })


@login_required
def export_profile_data(request):
    """Profil verilerini export et (GDPR uyumluluğu için)"""
    
    try:
        # Kullanıcı verileri
        user_data = {
            'user_info': {
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone': getattr(request.user, 'phone', ''),
                'user_type': getattr(request.user, 'user_type', ''),
                'date_joined': request.user.date_joined.isoformat(),
                'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
            }
        }
        
        # Profil verileri
        if hasattr(request.user, 'jobseeker_profile'):
            profile = request.user.jobseeker_profile
            user_data['profile'] = {
                'type': 'jobseeker',
                'city': getattr(profile, 'city', ''),
                'bio': getattr(profile, 'bio', ''),
                'skills': getattr(profile, 'skills', ''),
                'experience_years': getattr(profile, 'experience_years', 0),
                'is_available': getattr(profile, 'is_available', True),
            }
            
        elif hasattr(request.user, 'business_profile'):
            profile = request.user.business_profile
            user_data['profile'] = {
                'type': 'business',
                'company_name': getattr(profile, 'company_name', ''),
                'city': getattr(profile, 'city', ''),
                'address': getattr(profile, 'address', ''),
                'website': getattr(profile, 'website', ''),
            }
        
        # JSON olarak export et
        response = HttpResponse(
            json.dumps(user_data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="profil_verileri_{request.user.id}.json"'
        
        logger.info(f"Profile data exported for: {request.user.email}")
        return response
        
    except Exception as e:
        logger.error(f"Export profile data error for {request.user.email}: {str(e)}")
        messages.error(request, 'Veri export edilirken hata oluştu.')
        return redirect('profiles:settings')


# Template entegrasyonu için HELPER fonksiyonlar
def get_profile_data(user):
    """Kullanıcının profil verilerini template için hazırla"""
    
    try:
        if hasattr(user, 'jobseeker_profile'):
            profile = user.jobseeker_profile
            profile_type = 'jobseeker'
            data = {
                'type': profile_type,
                'full_name': getattr(profile, 'full_name', user.get_full_name()),
                'city': getattr(profile, 'city', ''),
                'district': getattr(profile, 'district', ''),
                'experience_years': getattr(profile, 'experience_years', 0),
                'bio': getattr(profile, 'bio', ''),
                'skills': getattr(profile, 'skills', ''),
                'skills_list': getattr(profile, 'skills', '').split(',') if getattr(profile, 'skills', '') else [],
                'is_available': getattr(profile, 'is_available', True),
                'is_verified': getattr(profile, 'is_verified', False),
            }
        elif hasattr(user, 'business_profile'):
            profile = user.business_profile
            profile_type = 'business'
            data = {
                'type': profile_type,
                'business_name': getattr(profile, 'company_name', '') or getattr(profile, 'business_name', ''),
                'city': getattr(profile, 'city', ''),
                'district': getattr(profile, 'district', ''),
                'phone': getattr(profile, 'phone', ''),
                'address': getattr(profile, 'address', ''),
                'description': getattr(profile, 'description', ''),
                'website': getattr(profile, 'website', ''),
                'contact_person': getattr(profile, 'contact_person', user.get_full_name()),
                'is_verified': getattr(profile, 'is_verified', False),
            }
        else:
            # Varsayılan profil
            data = {
                'type': 'jobseeker',
                'full_name': user.get_full_name(),
                'city': '',
                'district': '',
                'experience_years': 0,
                'bio': '',
                'skills': '',
                'skills_list': [],
                'is_available': True,
                'is_verified': False,
            }
    except Exception as e:
        # Hata durumunda varsayılan veri
        data = {
            'type': 'jobseeker',
            'full_name': user.get_full_name(),
            'city': '',
            'district': '',
            'experience_years': 0,
            'bio': '',
            'skills': '',
            'skills_list': [],
            'is_available': True,
            'is_verified': False,
        }
    
    return data


def calculate_user_stats(user):
    """Kullanıcı istatistiklerini hesapla"""
    
    stats = {
        'join_date': user.date_joined,
        'last_active': getattr(user, 'last_login', None),
        'total_views': getattr(user, 'profile_views', 0),
    }
    
    profile_data = get_profile_data(user)
    
    if profile_data['type'] == 'jobseeker':
        # İş arayan istatistikleri
        try:
            total_applications = JobApplication.objects.filter(applicant=user).count()
            successful_applications = JobApplication.objects.filter(applicant=user, status='hired').count()
        except:
            total_applications = 0
            successful_applications = 0
            
        stats.update({
            'total_applications': total_applications,
            'successful_applications': successful_applications,
        })
    else:
        # İş veren istatistikleri
        try:
            total_job_posts = JobListing.objects.filter(business=user).count()
            active_job_posts = JobListing.objects.filter(business=user, status='active').count()
            total_applications_received = JobApplication.objects.filter(job__business=user).count()
        except:
            total_job_posts = 0
            active_job_posts = 0
            total_applications_received = 0
            
        stats.update({
            'total_job_posts': total_job_posts,
            'active_job_posts': active_job_posts,
            'total_applications_received': total_applications_received,
        })
    
    return stats


def calculate_profile_completion(user, profile_data):
    """Profil tamamlanma yüzdesini hesapla"""
    
    completed_fields = 0
    total_fields = 10
    
    # Temel alanları kontrol et
    if user.first_name: completed_fields += 1
    if user.last_name: completed_fields += 1
    if user.email: completed_fields += 1
    if profile_data.get('city'): completed_fields += 1
    
    if profile_data['type'] == 'jobseeker':
        if profile_data.get('full_name'): completed_fields += 1
        if profile_data.get('bio'): completed_fields += 1
        if profile_data.get('skills'): completed_fields += 1
        if profile_data.get('experience_years', 0) > 0: completed_fields += 1
        # İsteğe bağlı: profil fotoğrafı kontrolü
        # if hasattr(user, 'avatar') and user.avatar: completed_fields += 1
    else:
        if profile_data.get('business_name'): completed_fields += 1
        if profile_data.get('description'): completed_fields += 1
        if profile_data.get('address'): completed_fields += 1
        if profile_data.get('phone'): completed_fields += 1
    
    return min(int((completed_fields / total_fields) * 100), 100)


def get_completion_items(user, profile_data):
    """Tamamlanma öğelerini döndür"""
    
    items = []
    
    # Temel kontroller
    items.append({
        'label': 'Temel bilgiler tamamlandı',
        'completed': bool(user.first_name and user.last_name and user.email)
    })
    
    if profile_data['type'] == 'jobseeker':
        items.extend([
            {
                'label': 'Hakkımda bölümü dolduruldu',
                'completed': bool(profile_data.get('bio'))
            },
            {
                'label': 'Yetenekler eklendi',
                'completed': bool(profile_data.get('skills'))
            },
            {
                'label': 'Profil fotoğrafı ekle',
                'completed': False  # Bu kontrol için avatar alanınızı kontrol edin
            }
        ])
    else:
        items.extend([
            {
                'label': 'İşletme bilgileri tamamlandı',
                'completed': bool(profile_data.get('business_name') and profile_data.get('description'))
            },
            {
                'label': 'İletişim bilgileri eklendi',
                'completed': bool(profile_data.get('phone') and profile_data.get('address'))
            },
            {
                'label': 'Profil fotoğrafı ekle',
                'completed': False
            }
        ])
    
    return items


def get_recent_activities(user):
    """Son aktiviteleri döndür"""
    
    activities = []
    
    try:
        if hasattr(user, 'jobseeker_profile'):
            # İş arayan aktiviteleri
            recent_applications = JobApplication.objects.filter(
                applicant=user
            ).select_related('job').order_by('-applied_at')[:3]
            
            for app in recent_applications:
                activities.append({
                    'type': 'application',
                    'title': f"{app.job.title} pozisyonuna başvuru",
                    'company': app.job.business.get_full_name() if hasattr(app.job.business, 'get_full_name') else str(app.job.business),
                    'location': getattr(app.job, 'location', ''),
                    'status': app.status,
                    'date': app.applied_at
                })
        elif hasattr(user, 'business_profile'):
            # İş veren aktiviteleri
            recent_jobs = JobListing.objects.filter(
                business=user
            ).order_by('-created_at')[:3]
            
            for job in recent_jobs:
                activities.append({
                    'type': 'job_post',
                    'title': f"{job.title} ilanı yayınlandı",
                    'company': user.get_full_name(),
                    'location': getattr(job, 'location', ''),
                    'status': job.status,
                    'date': job.created_at
                })
    except:
        # Model bulunamazsa boş liste döndür
        pass
    
    return activities