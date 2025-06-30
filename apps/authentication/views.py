from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
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
from django.db.models import Q
from django.conf import settings # settings'i import etmeyi unutmayın

from .forms import SimpleLoginForm, SimpleRegisterForm
from .services import OTPService, SocialAuthService
from .models import CustomUser, OTPVerification, LoginHistory
from apps.profiles.models import JobSeekerProfile, BusinessProfile

logger = logging.getLogger(__name__)

# Yardımcı fonksiyon: IP adresini al
def get_client_ip(request):
    """IP adresini güvenli şekilde al"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_redirect_url_for_user(user):
    """Giriş sonrası yönlendirme"""
    # Admin'ler admin paneline
    if user.is_superuser or user.is_staff:
        return '/admin/'
    # Herkesi ana sayfaya yönlendir
    else:
        return '/posts/'  # Ana dashboard

def login_view(request):
    """Login sayfası ve işlemleri"""
    print(f"DEBUG: Login view çağrıldı, method: {request.method}")

    if request.user.is_authenticated:
        print("DEBUG: Kullanıcı zaten giriş yapmış")
        # Zaten giriş yapmış kullanıcıyı doğru sayfaya yönlendir
        return redirect(get_redirect_url_for_user(request.user))
    
    if request.method == 'POST':
        print("DEBUG: POST request alındı")
        form = SimpleLoginForm(request.POST)

        print(f"DEBUG: Form data: {request.POST}")
        print(f"DEBUG: Form geçerli mi: {form.is_valid()}")
        
        if form.is_valid():
            print("DEBUG: Form geçerli")
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            print(f"DEBUG: Email: {email}")
            print(f"DEBUG: Password var mı: {'Evet' if password else 'Hayır'}")

            try:
                # Email ile kullanıcıyı bul
                user_obj = CustomUser.objects.get(email=email)
                print(f"DEBUG: Kullanıcı bulundu: {user_obj.username}")
                
                # Username ile authenticate et
                user = authenticate(request, username=user_obj.username, password=password)
                print(f"DEBUG: Authenticate sonucu: {user}")
                
                if user is not None and user.is_active:
                    print("DEBUG: Kullanıcı aktif, login yapılıyor")
                    login(request, user)
                    
                    # Login history kaydet
                    LoginHistory.objects.create(
                        user=user, 
                        ip_address=get_client_ip(request), 
                        is_successful=True, 
                        login_method='password'
                    )
                    
                    # 3.A: Kullanıcının adını alıp hoş geldiniz mesajı oluştur
                    user_display_name = user.get_full_name() if user.get_full_name() else user.username
                    messages.success(request, f"Hoş geldiniz, {user_display_name}!") 
                    print("DEBUG: Login başarılı, redirect yapılıyor")
                    
                    # Öncelikle next parametresini kontrol et
                    next_url = request.GET.get('next') or request.POST.get('next')
                    if next_url and next_url.startswith('/') and not next_url.startswith('/auth/login'):
                        return redirect(next_url)
                    
                    # Kullanıcı tipine göre yönlendir
                    redirect_url = get_redirect_url_for_user(user)
                    print(f"DEBUG: Redirect URL: {redirect_url}")
                    return redirect(redirect_url)
                    
                elif user is not None and not user.is_active:
                    print("DEBUG: Kullanıcı aktif değil")
                    LoginHistory.objects.create(
                        user=user_obj, 
                        ip_address=get_client_ip(request), 
                        is_successful=False, 
                        login_method='password'
                    )
                    messages.error(request, 'Hesabınız aktif değil. Lütfen e-posta adresinizi doğrulayın.')
                else:
                    print("DEBUG: Şifre hatalı")
                    LoginHistory.objects.create(
                        user=user_obj, 
                        ip_address=get_client_ip(request), 
                        is_successful=False, 
                        login_method='password'
                    )
                    messages.error(request, 'Şifre hatalı. Lütfen tekrar deneyin.')
                    
            except CustomUser.DoesNotExist:
                print("DEBUG: Email ile kullanıcı bulunamadı")
                # Güvenlik için generic hata mesajı
                messages.error(request, 'E-posta adresi veya şifre hatalı.')
                
            except Exception as e:
                print(f"DEBUG: Login hatası: {str(e)}")
                logger.error(f"Login error: {str(e)}")
                messages.error(request, 'Giriş yapılırken bir hata oluştu. Lütfen tekrar deneyin.')
        else:
            print(f"DEBUG: Form geçersiz, hatalar: {form.errors}")
            messages.error(request, 'Lütfen form bilgilerini kontrol ediniz.')
            
    else:
        print("DEBUG: GET request, yeni form oluşturuluyor")
        form = SimpleLoginForm()

    print("DEBUG: Template render ediliyor")
    context = {
        'form': form,
        'page_title': 'Giriş Yap'
    }
    return render(request, 'auth/login.html', context)

def register_view(request):
    """Kayıt sayfası ve işlemleri"""
    if request.user.is_authenticated:
        return redirect(get_redirect_url_for_user(request.user))
    
    if request.method == 'POST':
        form = SimpleRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone')  # Phone opsiyonel olabilir
            password = form.cleaned_data['password']
            user_type = form.cleaned_data['user_type']

            # E-posta veya telefon kontrolü
            if CustomUser.objects.filter(Q(email=email) | Q(phone=phone)).exists():
                messages.error(request, 'Bu e-posta veya telefon numarası zaten kayıtlı.')
                return render(request, 'auth/register.html', {'form': form})
            
            try:
                # Yeni kullanıcı oluştur
                user = CustomUser.objects.create_user(
                    username=email if email else phone,
                    email=email,
                    phone=phone,
                    password=password,
                    user_type=user_type,
                    is_active=False,  # OTP doğrulaması sonrası aktif olacak
                    is_verified=False
                )

                # OTP gönderme işlemi
                otp_service = OTPService(user)
                otp_service.send_otp(send_email=bool(email), send_sms=bool(phone))

                messages.success(request, 'Kayıt başarılı! Hesabınızı doğrulamak için lütfen e-postanızı kontrol edin.')
                return redirect(reverse('auth:verify_otp_api') + f'?user_identifier={email if email else phone}')
            
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
            except Exception as e:
                logger.error(f"Kayıt hatası: {str(e)}")
                messages.error(request, 'Kayıt olurken bir hata oluştu. Lütfen tekrar deneyin.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = SimpleRegisterForm()
    
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    """Çıkış işlemi"""
    if request.user.is_authenticated:
        logout(request)
        # 3.B: Çıkış mesajı olarak düzeltildi
        messages.info(request, 'Başarıyla çıkış yaptınız.')
    # LOGOUT_REDIRECT_URL'ye yönlendir
    return redirect(settings.LOGOUT_REDIRECT_URL)

@csrf_exempt
@require_http_methods(["POST"])
def send_otp_api(request):
    """OTP gönderme API endpoint'i"""
    if request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Zaten giriş yapılmış.'}, status=400)
    
    try:
        data = json.loads(request.body)
        user_identifier = data.get('user_identifier')
        
        if not user_identifier:
            return JsonResponse({'success': False, 'message': 'E-posta veya telefon numarası gerekli.'}, status=400)
        
        user = CustomUser.objects.filter(Q(email=user_identifier) | Q(phone=user_identifier)).first()

        if not user:
            return JsonResponse({'success': False, 'message': 'Kullanıcı bulunamadı.'}, status=404)
        
        otp_service = OTPService(user)
        
        sent_email = False
        sent_sms = False
        if user.email:
            sent_email = otp_service.send_otp(send_email=True, send_sms=False)
        if user.phone:
            sent_sms = otp_service.send_otp(send_email=False, send_sms=True)

        if sent_email or sent_sms:
            return JsonResponse({'success': True, 'message': 'OTP gönderildi. Lütfen e-postanızı veya telefonunuzu kontrol edin.'})
        else:
            return JsonResponse({'success': False, 'message': 'OTP gönderilemedi. Kullanıcının e-posta veya telefon bilgisi eksik.'}, status=400)
            
    except Exception as e:
        logger.error(f"OTP gönderme hatası: {e}")
        return JsonResponse({'success': False, 'message': 'OTP gönderilirken bir hata oluştu.'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def verify_otp_api(request):
    """OTP doğrulama API endpoint'i"""
    try:
        data = json.loads(request.body)
        user_identifier = data.get('user_identifier')
        otp_code = data.get('otp_code')

        if not user_identifier or not otp_code:
            return JsonResponse({'success': False, 'message': 'Kullanıcı tanımlayıcı ve OTP kodu gerekli.'}, status=400)

        user = CustomUser.objects.filter(Q(email=user_identifier) | Q(phone=user_identifier)).first()

        if not user:
            return JsonResponse({'success': False, 'message': 'Kullanıcı bulunamadı.'}, status=404)

        otp_service = OTPService(user)
        
        if otp_service.verify_otp(otp_code):
            user.is_active = True
            user.is_verified = True
            if user.email == user_identifier:
                user.email_verified = True
            elif user.phone == user_identifier:
                user.phone_verified = True
            user.save()
            
            messages.success(request, 'Hesabınız başarıyla doğrulandı! Şimdi giriş yapabilirsiniz.')
            return JsonResponse({
                'success': True, 
                'message': 'OTP doğrulandı. Hesap aktif edildi.', 
                'redirect_url': reverse('auth:login')
            })
        else:
            return JsonResponse({'success': False, 'message': 'Geçersiz veya süresi dolmuş OTP kodu.'}, status=400)
            
    except Exception as e:
        logger.error(f"OTP doğrulama hatası: {e}")
        return JsonResponse({'success': False, 'message': 'OTP doğrulanırken bir hata oluştu.'}, status=500)

def password_reset_request(request):
    """Şifre sıfırlama talep sayfası"""
    if request.user.is_authenticated:
        return redirect(get_redirect_url_for_user(request.user))
    
    if request.method == 'POST':
        form = SimpleLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = CustomUser.objects.get(Q(email=username) | Q(phone=username))
                
                otp_service = OTPService(user)
                sent_email = False
                sent_sms = False
                
                if user.email:
                    sent_email = otp_service.send_otp(send_email=True, send_sms=False, purpose='password_reset')
                if user.phone:
                    sent_sms = otp_service.send_otp(send_email=False, send_sms=True, purpose='password_reset')

                if sent_email or sent_sms:
                    messages.success(request, 'Şifre sıfırlama kodu gönderildi. Lütfen e-postanızı veya telefonunuzu kontrol edin.')
                    return redirect(reverse('auth:password_reset_verify') + f'?email={username}')
                else:
                    messages.error(request, 'Şifre sıfırlama kodu gönderilemedi. Kullanıcının e-posta veya telefon bilgisi eksik.')
                    
            except CustomUser.DoesNotExist:
                messages.error(request, 'Bu e-posta veya telefon numarasına kayıtlı kullanıcı bulunamadı.')
            except Exception as e:
                logger.error(f"Password reset request error: {str(e)}")
                messages.error(request, 'Şifre sıfırlama talebi oluşturulurken hata oluştu.')
    else:
        form = SimpleLoginForm()
        
    return render(request, 'auth/password_reset_request.html', {'form': form})

def password_reset_verify(request):
    """Şifre sıfırlama doğrulama sayfası ve şifre güncelleme"""
    if request.user.is_authenticated:
        return redirect(get_redirect_url_for_user(request.user))

    email = request.GET.get('email', '')
    message = "Lütfen gönderilen doğrulama kodunu girin ve yeni şifrenizi belirleyin."

    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        otp_code = request.POST.get('otp_code')
        
        if new_password != confirm_password:
            messages.error(request, 'Şifreler eşleşmiyor.')
            return render(request, 'auth/password_reset_verify.html', {'email': email, 'otp_code': otp_code})

        try:
            user = CustomUser.objects.get(Q(email=email) | Q(phone=email))

            otp_service = OTPService(user)
            if otp_service.verify_otp(otp_code, purpose='password_reset'):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Şifreniz başarıyla güncellendi! Şimdi giriş yapabilirsiniz.')
                return redirect('auth:login')
            else:
                messages.error(request, 'Geçersiz veya süresi dolmuş doğrulama kodu.')
                return render(request, 'auth/password_reset_verify.html', {'email': email, 'otp_code': otp_code})
                
        except CustomUser.DoesNotExist:
            messages.error(request, 'Kullanıcı bulunamadı.')
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            messages.error(request, 'Şifre güncellenirken hata oluştu.')
    else:
        message = "Yeni şifrenizi belirleyin."
    
    return render(request, 'auth/password_reset_verify.html', {'email': email, 'message': message})

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
        messages.warning(request, 'Kullanıcı türü belirlenmemiş. Lütfen yöneticinizle iletişime geçin.')
        return redirect('/posts/')

# Social Authentication Callbacks
def google_auth(request):
    """Google OAuth başlatma"""
    social_auth_service = SocialAuthService('google')
    auth_url = social_auth_service.get_authorization_url()
    return redirect(auth_url)

def google_callback(request):
    """Google OAuth callback"""
    social_auth_service = SocialAuthService('google')
    code = request.GET.get('code')
    
    try:
        user = social_auth_service.handle_callback(code, request)
        if user:
            login(request, user)
            messages.success(request, 'Google ile başarıyla giriş yaptınız!')
            return redirect(get_redirect_url_for_user(user))
        else:
            messages.error(request, 'Google ile giriş yapılamadı.')
            return redirect('auth:login')
    except Exception as e:
        logger.error(f"Google callback error: {e}")
        messages.error(request, f"Google ile giriş hatası: {e}")
        return redirect('auth:login')

def linkedin_auth(request):
    """LinkedIn OAuth başlatma"""
    social_auth_service = SocialAuthService('linkedin')
    auth_url = social_auth_service.get_authorization_url()
    return redirect(auth_url)

def linkedin_callback(request):
    """LinkedIn OAuth callback"""
    social_auth_service = SocialAuthService('linkedin')
    code = request.GET.get('code')
    
    try:
        user = social_auth_service.handle_callback(code, request)
        if user:
            login(request, user)
            messages.success(request, 'LinkedIn ile başarıyla giriş yaptınız!')
            return redirect(get_redirect_url_for_user(user))
        else:
            messages.error(request, 'LinkedIn ile giriş yapılamadı.')
            return redirect('auth:login')
    except Exception as e:
        logger.error(f"LinkedIn callback error: {e}")
        messages.error(request, f"LinkedIn ile giriş hatası: {e}")
        return redirect('auth:login')