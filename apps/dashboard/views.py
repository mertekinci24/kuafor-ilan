from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from apps.jobs.models import Job
from apps.profiles.models import Profile

User = get_user_model()

@login_required
def dashboard_view(request):
    user = request.user
    
    # İstatistikler
    if user.user_type == 'business':
        total_jobs = Job.objects.filter(employer=user).count()
        active_applications = Job.objects.filter(employer=user, applications__isnull=False).count()
        stats = {
            'total_jobs': total_jobs,
            'active_applications': active_applications,
            'new_members': User.objects.filter(user_type='job_seeker').count(),
            'total_revenue': 2450
        }
    else:
        applied_jobs = user.applications.count() if hasattr(user, 'applications') else 0
        stats = {
            'applied_jobs': applied_jobs,
            'profile_views': 89,
            'saved_jobs': 12,
            'messages': 5
        }
    
    # Son aktiviteler
    recent_jobs = Job.objects.all()[:5]
    recent_users = User.objects.all()[:5]
    
    context = {
        'user': user,
        'stats': stats,
        'recent_jobs': recent_jobs,
        'recent_users': recent_users
    }
    
    return render(request, 'dashboard/dashboard.html', context)
  
