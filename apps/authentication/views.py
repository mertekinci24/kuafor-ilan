from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.urls import reverse
import json
import logging

from .forms import SimpleLoginForm, SimpleRegisterForm
from .services import OTPService, SocialAuthService
from .models import CustomUser, JobSeekerProfile, BusinessProfile

User = get_user_model()
logger = logging.getLogger(__name__)


def login_view(request):
    """Login sayfası ve işlemleri"""
    if request.user.is_authenticated:
        return redirect('/')  # Ana sayfaya yönlendir
    
    if request.method == 'POST':
        form = SimpleLoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = request.POST.get('remember_me')
            
            # Email veya telefon ile authenticate
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Remember me
                    if not remember_me:
                        request.session.set_expiry(0)  # Browser kapanınca sil
                    
                    # Giriş log'u
                    logger.info(f"User logged in: {user.email}")
                    
                    # Redirect
                    next_url = request.GET.get('next', '/')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Hesabınız deaktive edilmiş.')
            else:
                messages.error(request, 'E-posta/telefon veya şifre hatalı.')
        else:
            messages.error(request, 'Lütfen formu doğru doldurun.')
    else:
        form = SimpleLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def register_view(request):
    """Kayıt sayfası ve işlemleri"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = SimpleRegisterForm(request.POST)
        
        if form.is_valid():
            try:
                # Kullanıcı oluştur
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    user_type=form.cleaned_data['user_type']
                )
                
                # Profil oluştur
                create_user_profile(user)
                
                # Otomatik giriş yap
                login(request, user)
                
                messages.success(request, 'Hesabınız başarıyla oluşturuldu! Hoş geldiniz.')
                logger.info(f"New user registered: {user.email}")
                
                return redirect('/')
                
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                messages.error(request, 'Kayıt sırasında bir hata oluştu.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SimpleRegisterForm()
    
    return render(request, 'auth/register.html', {'form': form})


def create_user_profile(user):
    """Kullanıcı tipine göre profil oluştur"""
    if user.user_type == 'jobseeker':
        JobSeekerProfile.objects.create(
            user=user,
            full_name=f"{user.first_name} {user.last_name}",
            city="İstanbul"  # Varsayılan
        )
    elif user.user_type == 'business':
        BusinessProfile.objects.create(
            user=user,
            business_name=f"{user.first_name} {user.last_name}",
            city="İstanbul",
            phone=user.phone or "",
            address="Belirtilmemiş"
        )


@login_required
def logout_view(request):
    """Çıkış işlemi"""
    user_email = request.user.email
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    logger.info(f"User logged out: {user_email}")
    return redirect('home')


# API Views for OTP
@csrf_exempt
@require_http_methods(["POST"])
def send_otp_api(request):
    """OTP gönderme API"""
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        email_address = data.get('email_address')
        otp_type = data.get('otp_type', 'login')
        
        if not phone_number and not email_address:
            return JsonResponse({
                'success': False,
                'message': 'Telefon numarası veya e-posta gerekli'
            })
        
        # OTP gönder
        success, otp_record, message = OTPService.create_otp(
            phone_number=phone_number,
            email_address=email_address,
            otp_type=otp_type,
            request=request
        )
        
        return JsonResponse({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Send OTP API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'OTP gönderilirken hata oluştu'
        })


@csrf_exempt
@require_http_methods(["POST"])
def verify_otp_api(request):
    """OTP doğrulama API"""
    try:
        data = json.loads(request.body)
        otp_code = data.get('otp_code')
        phone_number = data.get('phone_number')
        email_address = data.get('email_address')
        otp_type = data.get('otp_type', 'login')
        
        if not otp_code:
            return JsonResponse({
                'success': False,
                'message': 'OTP kodu gerekli'
            })
        
        # OTP doğrula
        success, otp_record, message = OTPService.verify_otp(
            otp_code=otp_code,
            phone_number=phone_number,
            email_address=email_address,
            otp_type=otp_type
        )
        
        if success and otp_type == 'login':
            # Kullanıcıyı bul veya oluştur
            if phone_number:
                user, created = User.objects.get_or_create(
                    phone=phone_number,
                    defaults={
                        'username': phone_number,
                        'phone_verified': True
                    }
                )
            else:
                user, created = User.objects.get_or_create(
                    email=email_address,
                    defaults={
                        'username': email_address,
                        'email_verified': True
                    }
                )
            
            if created:
                create_user_profile(user)
            
            # Giriş yap
            login(request, user)
            
        return JsonResponse({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Verify OTP API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'OTP doğrulanırken hata oluştu'
        })


# Social Auth Views
def google_auth(request):
    """Google OAuth başlatma"""
    # TODO: Google OAuth implementasyonu
    messages.info(request, 'Google ile giriş özelliği yakında eklenecek!')
    return redirect('authentication:login')


def linkedin_auth(request):
    """LinkedIn OAuth başlatma"""
    # TODO: LinkedIn OAuth implementasyonu
    messages.info(request, 'LinkedIn ile giriş özelliği yakında eklenecek!')
    return redirect('authentication:login')


def google_callback(request):
    """Google OAuth callback"""
    # TODO: Google OAuth callback
    messages.error(request, 'OAuth callback henüz yapılandırılmamış.')
    return redirect('authentication:login')


def linkedin_callback(request):
    """LinkedIn OAuth callback"""
    # TODO: LinkedIn OAuth callback
    messages.error(request, 'OAuth callback henüz yapılandırılmamış.')
    return redirect('authentication:login')


# Password Reset Views
def password_reset_request(request):
    """Şifre sıfırlama isteği"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # OTP gönder
            success, otp_record, message = OTPService.create_otp(
                email_address=email,
                otp_type='password_reset',
                user=user,
                request=request
            )
            
            if success:
                request.session['reset_email'] = email
                return redirect('authentication:password_reset_verify')
            else:
                messages.error(request, message)
                
        except User.DoesNotExist:
            messages.error(request, 'Bu e-posta adresi ile kayıtlı kullanıcı bulunamadı.')
    
    return render(request, 'auth/password_reset.html')


def password_reset_verify(request):
    """Şifre sıfırlama OTP doğrulama"""
    email = request.session.get('reset_email')
    if not email:
        return redirect('authentication:password_reset_request')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        new_password = request.POST.get('new_password')
        
        # OTP doğrula
        success, otp_record, message = OTPService.verify_otp(
            otp_code=otp_code,
            email_address=email,
            otp_type='password_reset'
        )
        
        if success:
            # Şifreyi güncelle
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            del request.session['reset_email']
            messages.success(request, 'Şifreniz başarıyla güncellendi.')
            return redirect('authentication:login')
        else:
            messages.error(request, message)
    
    return render(request, 'auth/password_reset_verify.html', {'email': email})


# Profile Views (buraya taşındı çünkü authentication ile ilgili)
@login_required
def profile_redirect(request):
    """Profil yönlendirme"""
    return redirect('profiles:profile')


@login_required 
def dashboard_redirect(request):
    """Dashboard yönlendirme"""
    return redirect('dashboard:home')
    
