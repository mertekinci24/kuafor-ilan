from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json
import random

from apps.authentication.models import CustomUser, JobSeekerProfile, BusinessProfile


@login_required
def dashboard_home(request):
    """Ana dashboard sayfası"""
    user = request.user
    
    # Kullanıcı tipine göre dashboard context'i hazırla
    if user.user_type == 'jobseeker':
        context = get_jobseeker_dashboard_context(user)
    else:
        context = get_business_dashboard_context(user)
    
    # Ortak context bilgileri
    context.update({
        'user': user,
        'current_time': timezone.now(),
        'user_avatar': user.first_name[0].upper() if user.first_name else 'U',
    })
    
    return render(request, 'dashboard/dashboard.html', context)


def get_jobseeker_dashboard_context(user):
    """İş arayan için dashboard context'i"""
    try:
        profile = user.jobseeker_profile
    except JobSeekerProfile.DoesNotExist:
        # Profil yoksa oluştur
        profile = JobSeekerProfile.objects.create(
            user=user,
            city='İstanbul',
            experience_years='beginner'
        )
    
    # İstatistik verileri (simulated data)
    stats = {
        'stat1': profile.total_applications or random.randint(15, 50),
        'stat2': user.profile_views or random.randint(50, 200),
        'stat3': random.randint(5, 25),  # Kaydedilen ilanlar
        'stat4': random.randint(2, 15),  # Mesajlar
    }
    
    # Son aktiviteler (simulated)
    recent_activities = [
        {
            'avatar': 'GS',
            'userName': 'Güzellik Salonu',
            'action': 'başvurunuzu inceledi',
            'time': '2 saat önce',
            'status': 'pending'
        },
        {
            'avatar': 'MB',
            'userName': 'Modern Berber',
            'action': 'profilinizi görüntüledi',
            'time': '5 saat önce',
            'status': 'success'
        },
        {
            'avatar': 'HS',
            'userName': 'Hair Studio',
            'action': 'ilanına başvurdunuz',
            'time': '1 gün önce',
            'status': 'success'
        }
    ]
    
    # Önerilen ilanlar (simulated)
    recommended_jobs = [
        {
            'icon': '💇',
            'title': 'Deneyimli Kuaför Aranıyor',
            'location': 'İstanbul, Kadıköy',
            'status': 'new'
        },
        {
            'icon': '✂️',
            'title': 'Berber - Part Time',
            'location': 'İstanbul, Şişli',
            'status': 'urgent'
        },
        {
            'icon': '💄',
            'title': 'Güzellik Uzmanı',
            'location': 'İstanbul, Beşiktaş',
            'status': 'active'
        }
    ]
    
    return {
        'stats': stats,
        'recent_activities': recent_activities,
        'recommended_jobs': recommended_jobs,
        'profile': profile,
        'user_type': 'jobseeker',
        'dashboard_title': 'Başvuru Aktivitesi',
        'activity_title': 'Son Aktiviteler',
        'jobs_title': 'Önerilen İlanlar',
    }


def get_business_dashboard_context(user):
    """İş veren için dashboard context'i"""
    try:
        profile = user.business_profile
    except BusinessProfile.DoesNotExist:
        # Profil yoksa oluştur
        profile = BusinessProfile.objects.create(
            user=user,
            company_name=f"{user.get_full_name()} Şirketi",
            establishment_year=timezone.now().year,
            city='İstanbul',
            address='',
            contact_person=user.get_full_name(),
            contact_phone=user.phone or ''
        )
    
    # İstatistik verileri (simulated data)
    stats = {
        'stat1': profile.total_job_posts or random.randint(5, 25),
        'stat2': profile.total_applications_received or random.randint(50, 200),
        'stat3': random.randint(10, 50),  # Yeni üyeler
        'stat4': random.randint(5000, 25000),  # Toplam gelir
    }
    
    # Son başvurular (simulated)
    recent_applications = [
        {
            'avatar': 'AY',
            'userName': 'Ayşe Yılmaz',
            'action': 'kuaför pozisyonuna başvurdu',
            'time': '2 saat önce',
            'status': 'pending'
        },
        {
            'avatar': 'MK',
            'userName': 'Mehmet Kaya',
            'action': 'berber pozisyonuna başvurdu',
            'time': '4 saat önce',
            'status': 'success'
        },
        {
            'avatar': 'EÖ',
            'userName': 'Elif Özkan',
            'action': 'güzellik uzmanı pozisyonuna başvurdu',
            'time': '6 saat önce',
            'status': 'pending'
        }
    ]
    
    # İlanlarım (simulated)
    my_jobs = [
        {
            'icon': '🏢',
            'title': 'Güzellik Salonu - Kuaför Aranıyor',
            'location': 'İstanbul, Kadıköy',
            'status': 'active'
        },
        {
            'icon': '💇',
            'title': 'Modern Berber - Deneyimli Berber',
            'location': 'İstanbul, Şişli',
            'status': 'active'
        },
        {
            'icon': '✨',
            'title': 'Hair Studio - Saç Uzmanı',
            'location': 'İstanbul, Beşiktaş',
            'status': 'pending'
        }
    ]
    
    return {
        'stats': stats,
        'recent_activities': recent_applications,
        'recommended_jobs': my_jobs,
        'profile': profile,
        'user_type': 'business',
        'dashboard_title': 'İlan Performansı',
        'activity_title': 'Son Başvurular',
        'jobs_title': 'İlanlarım',
    }


@login_required
def get_dashboard_stats(request):
    """Dashboard istatistiklerini JSON olarak döndür (AJAX için)"""
    user = request.user
    
    if user.user_type == 'jobseeker':
        try:
            profile = user.jobseeker_profile
            stats = {
                'applications': profile.total_applications,
                'profile_views': user.profile_views,
                'saved_jobs': random.randint(5, 25),
                'messages': random.randint(2, 15),
            }
        except JobSeekerProfile.DoesNotExist:
            stats = {
                'applications': 0,
                'profile_views': 0,
                'saved_jobs': 0,
                'messages': 0,
            }
    else:
        try:
            profile = user.business_profile
            stats = {
                'total_jobs': profile.total_job_posts,
                'applications_received': profile.total_applications_received,
                'new_members': random.randint(10, 50),
                'revenue': random.randint(5000, 25000),
            }
        except BusinessProfile.DoesNotExist:
            stats = {
                'total_jobs': 0,
                'applications_received': 0,
                'new_members': 0,
                'revenue': 0,
            }
    
    return JsonResponse(stats)


@login_required
def get_chart_data(request, period='7'):
    """Chart verileri döndür"""
    # Simulated chart data
    chart_data = {
        '7': {
            'labels': ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'],
            'data': [random.randint(5, 30) for _ in range(7)]
        },
        '30': {
            'labels': ['Hft 1', 'Hft 2', 'Hft 3', 'Hft 4'],
            'data': [random.randint(50, 100) for _ in range(4)]
        },
        '90': {
            'labels': ['Oca', 'Şub', 'Mar'],
            'data': [random.randint(150, 250) for _ in range(3)]
        }
    }
    
    return JsonResponse(chart_data.get(period, chart_data['7']))


@login_required
def export_dashboard_data(request, format_type='json'):
    """Dashboard verilerini export et"""
    user = request.user
    
    # Dashboard verilerini topla
    if user.user_type == 'jobseeker':
        context = get_jobseeker_dashboard_context(user)
    else:
        context = get_business_dashboard_context(user)
    
    export_data = {
        'user_info': {
            'name': user.get_full_name(),
            'email': user.email,
            'user_type': user.get_user_type_display(),
            'plan': user.get_current_plan_display(),
        },
        'stats': context['stats'],
        'activities': context['recent_activities'],
        'jobs': context['recommended_jobs'],
        'export_date': timezone.now().isoformat(),
    }
    
    if format_type == 'json':
        return JsonResponse(export_data)
    else:
        # PDF ve Excel export'u client-side yapılacak
        return JsonResponse({'data': export_data})
        
