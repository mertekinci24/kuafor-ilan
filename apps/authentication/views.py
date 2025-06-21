from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import json

def login_view(request):
    """Login sayfası view'ı"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'E-posta ve şifre alanları zorunludur!')
            return render(request, 'auth/login.html')
        
        # Django'da email ile giriş için username olarak email kullanıyoruz
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, 'Giriş başarılı!')
                
                # Redirect to next URL if exists
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Hesabınız deaktif durumda!')
        else:
            messages.error(request, 'E-posta veya şifre hatalı!')
    
    return render(request, 'auth/login.html')

def register_view(request):
    """Register sayfası view'ı"""
    if request.method == 'POST':
        # Form verilerini al
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        city = request.POST.get('city', '').strip()
        experience = request.POST.get('experience', '0')
        password = request.POST.get('password', '')
        user_type = request.POST.get('user_type', 'jobseeker')
        plan = request.POST.get('plan', 'free')
        
        # Validation
        if not all([first_name, last_name, email, password, city]):
            messages.error(request, 'Tüm zorunlu alanları doldurun!')
            return render(request, 'auth/register.html')
        
        if len(password) < 8:
            messages.error(request, 'Şifre en az 8 karakter olmalıdır!')
            return render(request, 'auth/register.html')
        
        try:
            from .models import CustomUser
            
            # E-posta kontrolü
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Bu e-posta adresi zaten kullanılıyor!')
                return render(request, 'auth/register.html')
            
            # Username kontrolü (email ile aynı)
            if CustomUser.objects.filter(username=email).exists():
                messages.error(request, 'Bu e-posta adresi zaten kullanılıyor!')
                return render(request, 'auth/register.html')
            
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
                    experience_years=int(experience) if experience.isdigit() else 0
                )
                messages.success(request, 'İş arayan hesabınız başarıyla oluşturuldu! Giriş yapabilirsiniz.')
            
            elif user_type == 'business':
                from apps.profiles.models import BusinessProfile
                BusinessProfile.objects.create(
                    user=user,
                    business_name=f"{first_name} {last_name}",
                    city=city,
                    phone=phone,
                    address="Belirtilmemiş"
                )
                messages.success(request, 'İş veren hesabınız başarıyla oluşturuldu! Giriş yapabilirsiniz.')
            
            return redirect('authentication:login')
            
        except IntegrityError as e:
            messages.error(request, 'Bu bilgilerle bir hesap zaten mevcut!')
        except Exception as e:
            messages.error(request, f'Hesap oluşturulurken hata oluştu: {str(e)}')
    
    return render(request, 'auth/register.html')

@login_required
def logout_view(request):
    """Logout view'ı"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız!')
    return redirect('home')

def password_reset_view(request):
    """Şifre sıfırlama view'ı (gelecekte eklenecek)"""
    messages.info(request, 'Şifre sıfırlama özelliği yakında eklenecek!')
    return redirect('authentication:login')

@csrf_exempt  
def check_email_availability(request):
    """AJAX ile email müsaitlik kontrolü"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            if not email:
                return JsonResponse({'available': False, 'message': 'Email gerekli'})
            
            from .models import CustomUser
            exists = CustomUser.objects.filter(email=email).exists()
            
            return JsonResponse({
                'available': not exists,
                'message': 'Email müsait' if not exists else 'Email zaten kullanılıyor'
            })
        except Exception as e:
            return JsonResponse({'available': False, 'message': 'Hata oluştu'})
    
    return JsonResponse({'available': False, 'message': 'Geçersiz istek'})
    
