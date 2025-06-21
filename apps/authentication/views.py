from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def login_view(request):
    """Login sayfası view'ı"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Django'da email ile giriş için username olarak email kullanıyoruz
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Giriş başarılı!')
            return redirect('home')
        else:
            messages.error(request, 'E-posta veya şifre hatalı!')
    
    return render(request, 'auth/login.html')

def register_view(request):
    """Register sayfası view'ı"""
    if request.method == 'POST':
        # Form verilerini al
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        experience = request.POST.get('experience')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        plan = request.POST.get('plan', 'free')
        
        try:
            from .models import CustomUser
            
            # Kullanıcı oluştur
            user = CustomUser.objects.create_user(
                username=email,  # Email'i username olarak kullan
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                user_type=user_type
            )
            
            # Profil oluştur (user_type'a göre)
            if user_type == 'jobseeker':
                from apps.profiles.models import JobSeekerProfile
                JobSeekerProfile.objects.create(
                    user=user,
                    full_name=f"{first_name} {last_name}",
                    city=city,
                    experience_years=int(experience) if experience else 0
                )
            elif user_type == 'business':
                from apps.profiles.models import BusinessProfile
                BusinessProfile.objects.create(
                    user=user,
                    business_name=f"{first_name} {last_name}",
                    city=city,
                    phone=phone
                )
            
            messages.success(request, 'Hesabınız başarıyla oluşturuldu! Giriş yapabilirsiniz.')
            return redirect('authentication:login')
            
        except Exception as e:
            messages.error(request, f'Hesap oluşturulurken hata: {str(e)}')
    
    return render(request, 'auth/register.html')
@login_required
def logout_view(request):
    """Logout view'ı"""
    logout(request)
    messages.success(request, 'Çıkış yapıldı!')
    return redirect('home')
    
