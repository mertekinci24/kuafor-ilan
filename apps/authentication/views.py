from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
import json
import logging

from .forms import SimpleLoginForm, SimpleRegisterForm
from .services import OTPService, SocialAuthService
from .models import CustomUser, OTPVerification, LoginHistory
from apps.profiles.models import JobSeekerProfile, BusinessProfile

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
                    
                    # Login history kaydet
                    try:
                        LoginHistory.objects.create(
                            user=user,
                            ip_address=get_client_ip(request),
                            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                            is_successful=True,
                            login_method='password'
                        )
                    except Exception as e:
                        logger.error(f"Login history error: {str(e)}")
                    
                    # Giriş log'u
                    logger.info(f"User logged in: {user.email}")
                    
                    # Redirect
                    next_url = request.GET.get('next', '/')
                    messages.success(request, f'Hoş geldiniz, {user.get_full_name()}!')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Hesabınız deaktive edilmiş. Lütfen yönetici ile iletişime geçin.')
            else:
                # Başarısız giriş log'u
                try:
                    LoginHistory.objects.create(
                        user=None,  # Kullanıcı bulunamadı
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                        is_successful=False,
                        login_method='password'
                    )
                except Exception:
                    pass
                
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
                # Email benzersizlik kontrolü
                if User.objects.filter(email=form.cleaned_data['email']).exists():
                    messages.error(request, 'Bu e-posta adresi zaten kullanılıyor.')
                    return render(request, 'auth/register.html', {'form': form})
                
                # Kullanıcı oluştur
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    user_type=form.cleaned_data['user_type'],
                    phone=form.cleaned_data.get('phone', '')
                )
                
                # Profil oluştur
                create_user_profile(user)
                
                # Otomatik giriş yap
                login(request, user)
                
                # Login history kaydet
                try:
                    LoginHistory.objects.create(
                        user=user,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                        is_successful=True,
                        login_method='password'
                    )
                except Exception as e:
                    logger.error(f"Registration login history error: {str(e)}")
                
                messages.success(request, 'Hesabınız başarıyla oluşturuldu! Hoş geldiniz.')
                logger.info(f"New user registered: {user.email}")
                
                return redirect('/')
                
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                messages.error(request, 'Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SimpleRegisterForm()
    
    return render(request, 'auth/register.html', {'form': form})


def create_user_profile(user):
    """Kullanıcı tipine göre profil oluştur"""
    try:
        if user.user_type == 'jobseeker':
            if not hasattr(user, 'jobseeker_profile'):
                JobSeekerProfile.objects.create(
                    user=user,
                    city="İstanbul",  # Varsayılan
                    bio=f"Merhaba! Ben {user.get_full_name()}. İş arıyorum."
                )
        elif user.user_type == 'business':
            if not hasattr(user, 'business_profile'):
                BusinessProfile.objects.create(
                    user=user,
                    company_name=f"{user.first_name} {user.last_name}",
                    city="İstanbul",
                    address="Belirtilmemiş",
                    contact_person=user.get_full_name(),
                    contact_phone=user.phone or ""
                )
        
        logger.info(f"Profile created for user: {user.email} ({user.user_type})")
        
    except Exception as e:
        logger.error(f"Profile creation error for {user.email}: {str(e)}")


@login_required
def logout_view(request):
    """Çıkış işlemi"""
    user_email = request.user.email
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız. Tekrar görüşmek üzere!')
    logger.info(f"User logged out: {user_email}")
    return redirect('/')


# Utility Functions
def get_client_ip(request):
    """İstemci IP adresini al"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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
        
        # Rate limiting kontrolü
        recent_otps = OTPVerification.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
        )
        
        if phone_number:
            recent_otps = recent_otps.filter(phone_number=phone_number)
        else:
            recent_otps = recent_otps.filter(email_address=email_address)
        
        if recent_otps.count() >= 3:
            return JsonResponse({
                'success': False,
                'message': 'Çok fazla OTP isteği. Lütfen 1 dakika bekleyin.'
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
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Geçersiz JSON formatı'
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
                        'phone_verified': True,
                        'first_name': 'Kullanıcı',
                        'last_name': phone_number[-4:]  # Son 4 hanesi
                    }
                )
            else:
                user, created = User.objects.get_or_create(
                    email=email_address,
                    defaults={
                        'username': email_address,
                        'email_verified': True,
                        'first_name': 'Kullanıcı',
                        'last_name': email_address.split('@')[0][-4:]
                    }
                )
            
            if created:
                create_user_profile(user)
                logger.info(f"New user created via OTP: {user.email}")
            
            # Giriş yap
            login(request, user)
            
            # Login history kaydet
            try:
                LoginHistory.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    is_successful=True,
                    login_method='otp_sms' if phone_number else 'otp_email'
                )
            except Exception as e:
                logger.error(f"OTP login history error: {str(e)}")
            
        return JsonResponse({
            'success': success,
            'message': message
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Geçersiz JSON formatı'
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
    # TODO: Google OAuth callback implementasyonu
    messages.error(request, 'OAuth callback henüz yapılandırılmamış.')
    return redirect('authentication:login')


def linkedin_callback(request):
    """LinkedIn OAuth callback"""
    # TODO: LinkedIn OAuth callback implementasyonu
    messages.error(request, 'OAuth callback henüz yapılandırılmamış.')
    return redirect('authentication:login')


# Password Reset Views
def password_reset_request(request):
    """Şifre sıfırlama isteği"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            messages.error(request, 'E-posta adresi gerekli.')
            return render(request, 'auth/password_reset.html')
        
        try:
            user = User.objects.get(email=email)
            
            # Son 5 dakikada şifre sıfırlama isteği var mı?
            recent_requests = OTPVerification.objects.filter(
                user=user,
                otp_type='password_reset',
                created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
            )
            
            if recent_requests.exists():
                messages.warning(request, 'Son 5 dakikada zaten şifre sıfırlama kodu gönderildi.')
                return render(request, 'auth/password_reset.html')
            
            # OTP gönder
            success, otp_record, message = OTPService.create_otp(
                email_address=email,
                otp_type='password_reset',
                user=user,
                request=request
            )
            
            if success:
                request.session['reset_email'] = email
                messages.success(request, 'Şifre sıfırlama kodu e-posta adresinize gönderildi.')
                return redirect('authentication:password_reset_verify')
            else:
                messages.error(request, message)
                
        except User.DoesNotExist:
            # Güvenlik için kullanıcı bulunamasa da başarılı mesajı göster
            messages.success(request, 'Eğer bu e-posta adresi sistemde kayıtlıysa, şifre sıfırlama kodu gönderildi.')
            return render(request, 'auth/password_reset.html')
        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            messages.error(request, 'Şifre sıfırlama isteği gönderilirken hata oluştu.')
    
    return render(request, 'auth/password_reset.html')


def password_reset_verify(request):
    """Şifre sıfırlama OTP doğrulama"""
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Şifre sıfırlama oturumu bulunamadı. Lütfen tekrar deneyin.')
        return redirect('authentication:password_reset_request')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not otp_code:
            messages.error(request, 'OTP kodu gerekli.')
            return render(request, 'auth/password_reset_verify.html', {'email': email})
        
        if not new_password or len(new_password) < 8:
            messages.error(request, 'Şifre en az 8 karakter olmalıdır.')
            return render(request, 'auth/password_reset_verify.html', {'email': email})
        
        if new_password != confirm_password:
            messages.error(request, 'Şifreler eşleşmiyor.')
            return render(request, 'auth/password_reset_verify.html', {'email': email})
        
        # OTP doğrula
        success, otp_record, message = OTPService.verify_otp(
            otp_code=otp_code,
            email_address=email,
            otp_type='password_reset'
        )
        
        if success:
            try:
                # Şifreyi güncelle
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Session temizle
                if 'reset_email' in request.session:
                    del request.session['reset_email']
                
                messages.success(request, 'Şifreniz başarıyla güncellendi. Yeni şifrenizle giriş yapabilirsiniz.')
                logger.info(f"Password reset successful for: {email}")
                
                return redirect('authentication:login')
                
            except User.DoesNotExist:
                messages.error(request, 'Kullanıcı bulunamadı.')
            except Exception as e:
                logger.error(f"Password reset error: {str(e)}")
                messages.error(request, 'Şifre güncellenirken hata oluştu.')
        else:
            messages.error(request, message)
    
    return render(request, 'auth/password_reset_verify.html', {'email': email})


# Profile Views
@login_required
def profile_redirect(request):
    """Profil yönlendirme"""
    if hasattr(request.user, 'jobseeker_profile'):
        return redirect('/profiles/jobseeker/')
    elif hasattr(request.user, 'business_profile'):
        return redirect('/profiles/business/')
    else:
        messages.warning(request, 'Profiliniz oluşturulmamış. Lütfen profil bilgilerinizi tamamlayın.')
        return redirect('/profiles/create/')


@login_required 
def dashboard_redirect(request):
    """Dashboard yönlendirme"""
    if request.user.user_type == 'business':
        return redirect('/dashboard/business/')
    elif request.user.user_type == 'jobseeker':
        return redirect('/dashboard/jobseeker/')
    else:
        return redirect('/')  # Ana sayfaya yönlendir
