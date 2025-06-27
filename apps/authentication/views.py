from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout # get_user_model kaldırıldı
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
from django.db.models import Q # Q importu eklendi, çünkü kullanılıyor

from .forms import SimpleLoginForm, SimpleRegisterForm
from .services import OTPService, SocialAuthService
from .models import CustomUser, OTPVerification, LoginHistory # CustomUser doğrudan kullanılıyor
from apps.profiles.models import JobSeekerProfile, BusinessProfile

# User = get_user_model() # Bu satır kaldırıldı
logger = logging.getLogger(__name__)

# Yardımcı fonksiyon: IP adresini al
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login_view(request):
    """Login sayfası ve işlemleri"""
    if request.user.is_authenticated:
        return redirect('/')  # Ana sayfaya yönlendir
    
    if request.method == 'POST':
        form = SimpleLoginForm(request.POST)
        
        if form.is_valid():
            email_or_phone = form.cleaned_data.get('email_or_phone')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=email_or_phone, password=password)
            
            if user is not None:
                login(request, user)
                LoginHistory.objects.create(user=user, ip_address=get_client_ip(request), is_successful=True, login_method='password')
                messages.success(request, 'Başarıyla giriş yaptınız!')
                return redirect('/')
            else:
                # CustomUser modelini doğrudan kullanıyoruz
                LoginHistory.objects.create(user=CustomUser.objects.filter(Q(email=email_or_phone) | Q(phone=email_or_phone)).first(), ip_address=get_client_ip(request), is_successful=False, login_method='password')
                messages.error(request, 'Geçersiz e-posta/telefon veya şifre.')
    else:
        form = SimpleLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})

def register_view(request):
    """Kayıt sayfası ve işlemleri"""
    if request.user.is_authenticated:
        return redirect('/') # Ana sayfaya yönlendir
    
    if request.method == 'POST':
        form = SimpleRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            user_type = form.cleaned_data['user_type']

            # CustomUser modelini doğrudan kullanıyoruz
            if CustomUser.objects.filter(Q(email=email) | Q(phone=phone)).exists():
                messages.error(request, 'Bu e-posta veya telefon numarası zaten kayıtlı.')
                return render(request, 'auth/register.html', {'form': form})
            
            try:
                # CustomUser modelini doğrudan kullanıyoruz
                user = CustomUser.objects.create_user(
                    username=email if email else phone, # Kullanıcı adı olarak email veya telefon kullan
                    email=email,
                    phone=phone,
                    password=password,
                    user_type=user_type,
                    is_active=False, # Hesap doğrulana kadar aktif değil
                    is_verified=False
                )

                # OTP gönderme işlemi
                otp_service = OTPService(user)
                otp_service.send_otp(send_email=bool(email), send_sms=bool(phone)) # OTP'yi hem e-posta hem de SMS ile gönder

                messages.success(request, 'Kayıt başarılı! Hesabınızı doğrulamak için lütfen e-postanızı ve/veya telefonunuzu kontrol edin.')
                return redirect(reverse('authentication:verify_otp_api') + f'?user_identifier={email if email else phone}') # OTP doğrulama sayfasına yönlendir
            
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
        messages.info(request, 'Başarıyla çıkış yaptınız.')
    return redirect('authentication:login')

@csrf_exempt
@require_http_methods(["POST"])
def send_otp_api(request):
    """OTP gönderme API endpoint'i"""
    if request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Zaten giriş yapılmış.'}, status=400)
    
    data = json.loads(request.body)
    user_identifier = data.get('user_identifier') # email veya telefon numarası olabilir
    
    if not user_identifier:
        return JsonResponse({'success': False, 'message': 'E-posta veya telefon numarası gerekli.'}, status=400)
    
    # CustomUser modelini doğrudan kullanıyoruz
    user = CustomUser.objects.filter(Q(email=user_identifier) | Q(phone=user_identifier)).first()

    if not user:
        return JsonResponse({'success': False, 'message': 'Kullanıcı bulunamadı.'}, status=404)
    
    otp_service = OTPService(user)
    
    try:
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
    data = json.loads(request.body)
    user_identifier = data.get('user_identifier')
    otp_code = data.get('otp_code')

    if not user_identifier or not otp_code:
        return JsonResponse({'success': False, 'message': 'Kullanıcı tanımlayıcı ve OTP kodu gerekli.'}, status=400)

    # CustomUser modelini doğrudan kullanıyoruz
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
        return JsonResponse({'success': True, 'message': 'OTP doğrulandı. Hesap aktif edildi.', 'redirect_url': reverse('authentication:login')})
    else:
        return JsonResponse({'success': False, 'message': 'Geçersiz veya süresi dolmuş OTP kodu.'}, status=400)

def password_reset_request(request):
    """Şifre sıfırlama talep sayfası"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = SimpleLoginForm(request.POST) # LoginForm, email_or_phone alanını içeriyor
        if form.is_valid():
            email_or_phone = form.cleaned_data['email_or_phone']
            try:
                # CustomUser modelini doğrudan kullanıyoruz
                user = CustomUser.objects.get(Q(email=email_or_phone) | Q(phone=email_or_phone))
                
                otp_service = OTPService(user)
                sent_email = False
                sent_sms = False
                if user.email:
                    sent_email = otp_service.send_otp(send_email=True, send_sms=False, purpose='password_reset')
                if user.phone:
                    sent_sms = otp_service.send_otp(send_email=False, send_sms=True, purpose='password_reset')

                if sent_email or sent_sms:
                    messages.success(request, 'Şifre sıfırlama kodu gönderildi. Lütfen e-postanızı veya telefonunuzu kontrol edin.')
                    return redirect(reverse('authentication:password_reset_verify') + f'?email={email_or_phone}') # E-posta bilgisini token'a ekleyerek yönlendir
                else:
                    messages.error(request, 'Şifre sıfırlama kodu gönderilemedi. Kullanıcının e-posta veya telefon bilgisi eksik.')
            # CustomUser.DoesNotExist kullanıyoruz
            except CustomUser.DoesNotExist:
                messages.error(request, 'Bu e-posta veya telefon numarasına kayıtlı kullanıcı bulunamadı.')
            except Exception as e:
                logger.error(f"Password reset request error: {str(e)}")
                messages.error(request, 'Şifre sıfırlama talebi oluşturulurken hata oluştu.')
    else:
        form = SimpleLoginForm() # Sadece email_or_phone alanı içeren bir form
    return render(request, 'auth/password_reset_request.html', {'form': form})


def password_reset_verify(request):
    """Şifre sıfırlama doğrulama sayfası ve şifre güncelleme"""
    if request.user.is_authenticated:
        return redirect('/')

    email = request.GET.get('email', '') # URL'den e-posta bilgisini al
    message = "Lütfen gönderilen doğrulama kodunu girin ve yeni şifrenizi belirleyin."

    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        otp_code = request.POST.get('otp_code') # OTP kodu eklendi
        
        if new_password != confirm_password:
            messages.error(request, 'Şifreler eşleşmiyor.')
            return render(request, 'auth/password_reset_verify.html', {'email': email, 'otp_code': otp_code}) # otp_code'u da geri gönder

        try:
            # Email veya telefon numarası ile kullanıcıyı bul
            # CustomUser modelini doğrudan kullanıyoruz
            user = CustomUser.objects.get(Q(email=email) | Q(phone=email))

            otp_service = OTPService(user)
            if otp_service.verify_otp(otp_code, purpose='password_reset'):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Şifreniz başarıyla güncellendi! Şimdi giriş yapabilirsiniz.')
                return redirect('authentication:login')
            else:
                messages.error(request, 'Geçersiz veya süresi dolmuş doğrulama kodu.')
                return render(request, 'auth/password_reset_verify.html', {'email': email, 'otp_code': otp_code})
        # CustomUser.DoesNotExist kullanıyoruz
        except CustomUser.DoesNotExist:
            messages.error(request, 'Kullanıcı bulunamadı.')
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            messages.error(request, 'Şifre güncellenirken hata oluştu.')
    else:
        # Token doğrulama başarılı ise
        message = "Yeni şifrenizi belirleyin."
        # Token doğrulaması başarısız ise
        # message = "Geçersiz veya süresi dolmuş şifre sıfırlama linki."
    
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
        return redirect('/')

# Social Authentication Callbacks (assuming SocialAuthService handles User access internally)
def google_auth(request):
    social_auth_service = SocialAuthService('google')
    auth_url = social_auth_service.get_authorization_url()
    return redirect(auth_url)

def google_callback(request):
    social_auth_service = SocialAuthService('google')
    code = request.GET.get('code')
    try:
        user = social_auth_service.handle_callback(code, request) # Bu method CustomUser döndürmeli
        if user:
            login(request, user)
            messages.success(request, 'Google ile başarıyla giriş yaptınız!')
            return redirect('/')
        else:
            messages.error(request, 'Google ile giriş yapılamadı.')
            return redirect('authentication:login')
    except Exception as e:
        logger.error(f"Google callback error: {e}")
        messages.error(request, f"Google ile giriş hatası: {e}")
        return redirect('authentication:login')

def linkedin_auth(request):
    social_auth_service = SocialAuthService('linkedin')
    auth_url = social_auth_service.get_authorization_url()
    return redirect(auth_url)

def linkedin_callback(request):
    social_auth_service = SocialAuthService('linkedin')
    code = request.GET.get('code')
    try:
        user = social_auth_service.handle_callback(code, request) # Bu method CustomUser döndürmeli
        if user:
            login(request, user)
            messages.success(request, 'LinkedIn ile başarıyla giriş yaptınız!')
            return redirect('/')
        else:
            messages.error(request, 'LinkedIn ile giriş yapılamadı.')
            return redirect('authentication:login')
    except Exception as e:
        logger.error(f"LinkedIn callback error: {e}")
        messages.error(request, f"LinkedIn ile giriş hatası: {e}")
        return redirect('authentication:login')
    