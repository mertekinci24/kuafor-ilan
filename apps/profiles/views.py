from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import JobSeekerProfile, BusinessProfile
from apps.jobs.models import JobApplication, JobListing

User = get_user_model()

@login_required
def profile_view(request, user_id=None):
    """Profil görüntüleme sayfası"""
    
    # Eğer user_id verilmemişse, kendi profilini göster
    if user_id is None:
        user = request.user
    else:
        user = get_object_or_404(User, id=user_id)
    
    # Profil tipine göre profil verisini al
    profile = None
    profile_type = None
    
    if user.user_type == 'jobseeker':
        try:
            profile = user.jobseekerprofile
            profile_type = 'jobseeker'
        except:
            # Profil yoksa oluştur
            profile = JobSeekerProfile.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}",
                city="Belirtilmemiş"
            )
            profile_type = 'jobseeker'
    
    elif user.user_type == 'business':
        try:
            profile = user.businessprofile
            profile_type = 'business'
        except:
            # Profil yoksa oluştur
            profile = BusinessProfile.objects.create(
                user=user,
                business_name=f"{user.first_name} {user.last_name}",
                city="Belirtilmemiş",
                phone=user.phone or "",
                address="Belirtilmemiş"
            )
            profile_type = 'business'
    
    # İstatistikler
    stats = {}
    
    if profile_type == 'jobseeker':
        # İş arayan istatistikleri
        applications = JobApplication.objects.filter(applicant=user)
        stats = {
            'total_applications': applications.count(),
            'pending_applications': applications.filter(status='pending').count(),
            'accepted_applications': applications.filter(status='accepted').count(),
            'profile_views': 156,  # Şimdilik sabit değer
        }
        
        # Son başvurular
        recent_applications = applications.order_by('-created_at')[:5]
        
        context = {
            'profile_user': user,
            'profile': profile,
            'profile_type': profile_type,
            'stats': stats,
            'recent_applications': recent_applications,
            'is_own_profile': user == request.user,
        }
        
    elif profile_type == 'business':
        # İş veren istatistikleri
        job_listings = JobListing.objects.filter(business=user)
        all_applications = JobApplication.objects.filter(job__business=user)
        
        stats = {
            'total_jobs': job_listings.count(),
            'active_jobs': job_listings.filter(status='active').count(),
            'total_applications': all_applications.count(),
            'profile_views': 243,  # Şimdilik sabit değer
        }
        
        # Son ilanlar
        recent_jobs = job_listings.order_by('-created_at')[:5]
        
        context = {
            'profile_user': user,
            'profile': profile,
            'profile_type': profile_type,
            'stats': stats,
            'recent_jobs': recent_jobs,
            'is_own_profile': user == request.user,
        }
    
    return render(request, 'profiles/profile.html', context)

@login_required
def profile_edit_view(request):
    """Profil düzenleme sayfası"""
    
    # Kullanıcının profil tipine göre profil objesini al
    profile = None
    profile_type = request.user.user_type
    
    if profile_type == 'jobseeker':
        profile, created = JobSeekerProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'full_name': f"{request.user.first_name} {request.user.last_name}",
                'city': "Belirtilmemiş"
            }
        )
    elif profile_type == 'business':
        profile, created = BusinessProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'business_name': f"{request.user.first_name} {request.user.last_name}",
                'city': "Belirtilmemiş",
                'phone': request.user.phone or "",
                'address': "Belirtilmemiş"
            }
        )
    
    if request.method == 'POST':
        try:
            # Temel kullanıcı bilgileri güncelleme
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', request.user.email)
            request.user.phone = request.POST.get('phone', '')
            request.user.save()
            
            # Profil tipine göre özel alanları güncelle
            if profile_type == 'jobseeker':
                profile.full_name = request.POST.get('full_name', profile.full_name)
                profile.bio = request.POST.get('bio', '')
                profile.experience_years = int(request.POST.get('experience_years', 0) or 0)
                profile.skills = request.POST.get('skills', '')
                profile.city = request.POST.get('city', profile.city)
                profile.district = request.POST.get('district', '')
                profile.is_available = request.POST.get('is_available') == 'on'
                
            elif profile_type == 'business':
                profile.business_name = request.POST.get('business_name', profile.business_name)
                profile.description = request.POST.get('description', '')
                profile.address = request.POST.get('address', profile.address)
                profile.city = request.POST.get('city', profile.city)
                profile.district = request.POST.get('district', '')
                profile.phone = request.POST.get('phone', profile.phone)
                profile.website = request.POST.get('website', '')
            
            profile.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi!')
            return redirect('profiles:profile')
            
        except Exception as e:
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
    
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).order_by('-created_at')
    
    context = {
        'applications': applications,
    }
    
    return render(request, 'profiles/my_applications.html', context)

@login_required
def my_jobs_view(request):
    """İş verenin ilanlarını listele (sadece business için)"""
    
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
  
