from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json
import random


@login_required
def dashboard_home(request):
    """Ana dashboard sayfası - Basitleştirilmiş versiyon"""
    user = request.user
    
    # Basit context - authentication modelleri olmadan
    context = {
        'user': user,
        'current_time': timezone.now(),
        'user_avatar': user.first_name[0].upper() if user.first_name else 'U',
        'stats': {
            'stat1': random.randint(15, 50),
            'stat2': random.randint(50, 200),
            'stat3': random.randint(5, 25),
            'stat4': random.randint(2, 15),
        },
        'recent_activities': [
            {
                'avatar': 'GS',
                'userName': 'Güzellik Salonu',
                'action': 'sistemi inceledi',
                'time': '2 saat önce',
                'status': 'pending'
            },
            {
                'avatar': 'MB',
                'userName': 'Modern Berber',
                'action': 'platformu keşfetti',
                'time': '5 saat önce',
                'status': 'success'
            },
            {
                'avatar': 'HS',
                'userName': 'Hair Studio',
                'action': 'sisteme katıldı',
                'time': '1 gün önce',
                'status': 'success'
            }
        ],
        'recommended_jobs': [
            {
                'icon': '💇',
                'title': 'Platform Test',
                'location': 'İstanbul',
                'status': 'active'
            },
            {
                'icon': '✂️',
                'title': 'System Status',
                'location': 'Online',
                'status': 'active'
            },
            {
                'icon': '💄',
                'title': 'Beta Version',
                'location': 'Live',
                'status': 'active'
            }
        ],
        'user_type': 'jobseeker',
        'dashboard_title': 'Platform İstatistikleri',
        'activity_title': 'Son Aktiviteler',
        'jobs_title': 'Platform Durumu',
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def get_dashboard_stats(request):
    """Dashboard istatistiklerini JSON olarak döndür"""
    stats = {
        'applications': random.randint(10, 50),
        'profile_views': random.randint(50, 200),
        'saved_jobs': random.randint(5, 25),
        'messages': random.randint(2, 15),
    }
    
    return JsonResponse(stats)


@login_required
def get_chart_data(request, period='7'):
    """Chart verileri döndür"""
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
    export_data = {
        'user_info': {
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'user_type': 'Test User',
        },
        'stats': {
            'stat1': random.randint(10, 50),
            'stat2': random.randint(50, 200),
            'stat3': random.randint(5, 25),
            'stat4': random.randint(2, 15),
        },
        'export_date': timezone.now().isoformat(),
    }
    
    return JsonResponse(export_data)
    
