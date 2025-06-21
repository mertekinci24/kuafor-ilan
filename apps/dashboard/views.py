from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

@login_required
def dashboard_view(request):
    user = request.user
    
    # Kullanıcı tipine göre farklı istatistikler
    if hasattr(user, 'user_type') and user.user_type == 'business':
        stats = {
            'total_jobs': random.randint(10, 50),
            'active_applications': random.randint(20, 100),
            'new_members': random.randint(5, 25),
            'total_revenue': random.randint(5000, 20000)
        }
        
        # İşveren aktiviteleri
        recent_activities = [
            {
                'user_name': 'Ayşe Yılmaz',
                'action': 'kuaför pozisyonuna başvurdu',
                'time': '2 saat önce',
                'status': 'pending',
                'avatar': 'AY'
            },
            {
                'user_name': 'Mehmet Kaya',
                'action': 'berber pozisyonuna başvurdu', 
                'time': '4 saat önce',
                'status': 'success',
                'avatar': 'MK'
            },
            {
                'user_name': 'Elif Özkan',
                'action': 'yeni profil oluşturdu',
                'time': '6 saat önce', 
                'status': 'success',
                'avatar': 'EÖ'
            }
        ]
        
        recent_jobs = [
            {
                'title': 'Güzellik Salonu - Kuaför Aranıyor',
                'location': 'İstanbul, Kadıköy',
                'status': 'active',
                'icon': '🏢'
            },
            {
                'title': 'Modern Berber - Deneyimli Berber',
                'location': 'Ankara, Çankaya',
                'status': 'pending',
                'icon': '💇'
            },
            {
                'title': 'Hair Studio - Saç Uzmanı',
                'location': 'İzmir, Konak',
                'status': 'active',
                'icon': '✨'
            }
        ]
        
    else:
        # İş arayan istatistikleri
        stats = {
            'applied_jobs': random.randint(3, 15),
            'profile_views': random.randint(50, 200),
            'saved_jobs': random.randint(5, 30),
            'messages': random.randint(1, 10)
        }
        
        # İş arayan aktiviteleri
        recent_activities = [
            {
                'user_name': 'Güzel Saç Salonu',
                'action': 'başvurunuzu inceledi',
                'time': '1 saat önce',
                'status': 'success',
                'avatar': 'GS'
            },
            {
                'user_name': 'Modern Kuaför',
                'action': 'size mesaj gönderdi',
                'time': '3 saat önce',
                'status': 'pending',
                'avatar': 'MK'
            },
            {
                'user_name': 'Style Center',
                'action': 'profilinizi görüntüledi',
                'time': '5 saat önce',
                'status': 'success',
                'avatar': 'SC'
            }
        ]
        
        recent_jobs = [
            {
                'title': 'Deneyimli Kuaför Aranıyor',
                'location': 'İstanbul, Şişli',
                'status': 'new',
                'icon': '💇‍♀️'
            },
            {
                'title': 'Part-time Berber',
                'location': 'Ankara, Kızılay',
                'status': 'urgent',
                'icon': '✂️'
            },
            {
                'title': 'Saç Uzmanı - Tam Zamanlı',
                'location': 'İzmir, Alsancak',
                'status': 'new',
                'icon': '💁‍♀️'
            }
        ]
    
    # Genel kullanıcı bilgileri
    user_info = {
        'name': user.email.split('@')[0] if user.email else 'Admin User',
        'email': user.email or 'admin@kuaforilan.com',
        'avatar': user.email[0].upper() if user.email else 'A',
        'user_type': 'job_seeker'
    }
    
    # Chart verileri (örnek)
    chart_data = {
        'daily_views': [12, 19, 8, 15, 22, 18, 25],
        'applications': [5, 8, 12, 7, 15, 10, 18],
        'categories': {
            'Kuaför': 45,
            'Berber': 30,
            'Saç Uzmanı': 15,
            'Güzellik': 10
        }
    }
    
    context = {
        'user': user,
        'user_info': user_info,
        'stats': stats,
        'recent_activities': recent_activities,
        'recent_jobs': recent_jobs,
        'chart_data': chart_data,
        'current_time': timezone.now()
    }
    
    return render(request, 'dashboard/dashboard.html', context)
    
