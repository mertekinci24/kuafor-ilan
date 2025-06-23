from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json
import re

User = get_user_model()


@csrf_protect
def login_view(request):
    """Giriş sayfası"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        login_method = request.POST.get('login_method', 'email')
        
        if login_method == 'email':
            # Email ile normal giriş
            email = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # IP adresini kaydet
                user.last_login_ip = get_client_ip(request)
                user.save(update_fields=['last_login_ip'])
                
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Giriş bilgileriniz hatalı. Lütfen tekrar deneyin.')
        
        elif login_method == 'otp':
            # OTP ile giriş (JavaScript tarafından handle edilir)
            pass
    
    return render(request, 'auth/login.html')


@csrf_protect
def register_view(request):
    """Kayıt sayfası"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            user_type = request.POST.get('user_type', 'jobseeker')
            phone = request.POST.get('phone', '')
            
            # E-posta kontrolü
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Bu e-posta adresi zaten kullanılıyor.')
                return render(request, 'auth/register.html')
            
            # Telefon kontrolü (eğer girilmişse)
            if phone:
                phone = format_phone_number(phone)
                if User.objects.filter(phone=phone).exists():
                    messages.error(request, 'Bu telefon numarası zaten kullanılıyor.')
                    return render(request, 'auth/register.html')
            
            # Kullanıcı oluştur
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type,
                phone=phone if phone else None
            )
            
            # Otomatik giriş yap
            user = authenticate(request, username=email, password=password)
            login(request, user)
            
            messages.success(request, 'Hesabınız başarıyla oluşturuldu!')
            return redirect('dashboard:home')
            
        except Exception as e:
            messages.error(request, f'Hesap oluşturulurken bir hata oluştu: {str(e)}')
    
    return render(request, 'auth/register.html')


@login_required
def logout_view(request):
    """Çıkış"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('home')


@login_required
def profile_view(request):
    """Profil sayfası"""
    return render(request, 'auth/profile.html', {'user': request.user})


@require_http_methods(["POST"])
def check_email_exists(request):
    """E-posta adresinin kullanılıp kullanılmadığını kontrol et"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({'error': 'E-posta adresi gereklidir.'}, status=400)
        
        exists = User.objects.filter(email=email).exists()
        
        return JsonResponse({
            'exists': exists,
            'message': 'Bu e-posta adresi zaten kullanılıyor.' if exists else 'E-posta adresi kullanılabilir.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz JSON verisi.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Bir hata oluştu.'}, status=500)


@login_required
@require_http_methods(["POST"])
def update_profile_api(request):
    """Profil bilgilerini güncelle - API"""
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Güncellenebilir alanlar
        updatable_fields = ['first_name', 'last_name', 'phone']
        updated_fields = []
        
        for field in updatable_fields:
            if field in data:
                value = data[field].strip() if isinstance(data[field], str) else data[field]
                if field == 'phone' and value:
                    value = format_phone_number(value)
                if hasattr(user, field):
                    setattr(user, field, value)
                    updated_fields.append(field)
        
        # E-posta güncelleme (özel kontrol)
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if new_email != user.email:
                if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Bu e-posta adresi zaten kullanılıyor.'
                    }, status=400)
                
                user.email = new_email
                user.username = new_email
                updated_fields.extend(['email', 'username'])
        
        if updated_fields:
            user.save(update_fields=updated_fields + ['updated_at'])
            
            return JsonResponse({
                'success': True,
                'message': 'Profil bilgileriniz başarıyla güncellendi.',
                'updated_fields': updated_fields,
                'updated_name': user.get_full_name()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Güncellenecek bilgi bulunamadı.'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Geçersiz JSON verisi.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Profil güncellenirken bir hata oluştu: {str(e)}'
        }, status=500)


# ================================
# OTP API ENDPOINTS
# ================================

@require_http_methods(["POST"])
def send_otp_api(request):
    """OTP kodu gönder - API"""
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number', '').strip()
        email_address = data.get('email_address', '').strip()
        otp_type = data.get('otp_type', 'login')
        
        # Telefon veya email kontrolü
        if not phone_number and not email_address:
            return JsonResponse({
                'success': False,
                'error': 'Telefon numarası veya e-posta adresi gereklidir.'
            }, status=400)
        
        # Telefon numarası formatla
        if phone_number:
            phone_number = format_phone_number(phone_number)
            
            # Telefon numarası kayıtlı mı kontrol et
            user = User.objects.filter(phone=phone_number).first()
            if not user and otp_type == 'login':
                return JsonResponse({
                    'success': False,
                    'error': 'Bu telefon numarası ile kayıtlı kullanıcı bulunamadı.'
                }, status=404)
        
        # Email kontrolü
        if email_address:
            user = User.objects.filter(email=email_address).first()
            if not user and otp_type == 'login':
                return JsonResponse({
                    'success': False,
                    'error': 'Bu e-posta adresi ile kayıtlı kullanıcı bulunamadı.'
                }, status=404)
        
        # Rate limiting - Son 1 dakikada gönderilmiş OTP var mı?
        from .models import OTPVerification
        recent_otp = OTPVerification.objects.filter(
            phone_number=phone_number if phone_number else None,
            email_address=email_address if email_address else None,
            created_at__gte=timezone.now() - timedelta(minutes=1)
        ).first()
        
        if recent_otp:
            return JsonResponse({
                'success': False,
                'error': 'Çok sık OTP isteği gönderiyorsunuz. 1 dakika bekleyin.'
            }, status=429)
        
        # OTP oluştur ve gönder
        from .services import OTPService
        success, otp_record, message = OTPService.create_otp(
            phone_number=phone_number,
            email_address=email_address,
            otp_type=otp_type,
            user=user,
            request=request
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'expires_in': 300  # 5 dakika
            })
        else:
            return JsonResponse({
                'success': False,
                'error': message
            }, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Geçersiz JSON verisi.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'OTP gönderilirken hata: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def verify_otp_api(request):
    """OTP kodunu doğrula ve giriş yap - API"""
    try:
        data = json.loads(request.body)
        otp_code = data.get('otp_code', '').strip()
        phone_number = data.get('phone_number', '').strip()
        email_address = data.get('email_address', '').strip()
        otp_type = data.get('otp_type', 'login')
        
        # Gerekli alanlar
        if not otp_code:
            return JsonResponse({
                'success': False,
                'error': 'OTP kodu gereklidir.'
            }, status=400)
        
        if not phone_number and not email_address:
            return JsonResponse({
                'success': False,
                'error': 'Telefon numarası veya e-posta adresi gereklidir.'
            }, status=400)
        
        # Telefon numarası formatla
        if phone_number:
            phone_number = format_phone_number(phone_number)
        
        # OTP doğrula
        from .services import OTPService
        success, otp_record, message = OTPService.verify_otp(
            otp_code=otp_code,
            phone_number=phone_number,
            email_address=email_address,
            otp_type=otp_type
        )
        
        if not success:
            return JsonResponse({
                'success': False,
                'error': message
            }, status=400)
        
        # Kullanıcıyı bul ve giriş yap
        if phone_number:
            user = User.objects.filter(phone=phone_number).first()
        else:
            user = User.objects.filter(email=email_address).first()
        
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Kullanıcı bulunamadı.'
            }, status=404)
        
        # OTP ile giriş yap
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # IP adresini kaydet
        user.last_login_ip = get_client_ip(request)
        
        # Telefon doğrulamasını işaretle
        if phone_number:
            user.phone_verified = True
        else:
            user.email_verified = True
            
        user.save(update_fields=['last_login_ip', 'phone_verified', 'email_verified'])
        
        return JsonResponse({
            'success': True,
            'message': 'Giriş başarılı!',
            'redirect_url': '/dashboard/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Geçersiz JSON verisi.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'OTP doğrulama hatası: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def check_phone_exists(request):
    """Telefon numarasının kayıtlı olup olmadığını kontrol et"""
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number', '').strip()
        
        if not phone_number:
            return JsonResponse({'error': 'Telefon numarası gereklidir.'}, status=400)
        
        # Telefon numarasını formatla
        phone_number = format_phone_number(phone_number)
        
        # Kullanıcı var mı kontrol et
        user = User.objects.filter(phone=phone_number).first()
        
        return JsonResponse({
            'exists': bool(user),
            'phone_verified': user.phone_verified if user else False,
            'message': 'Telefon numarası kayıtlı' if user else 'Telefon numarası kayıtlı değil'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz JSON verisi.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Kontrol hatası: {str(e)}'}, status=500)


# ================================
# SOSYAL MEDYA LOGIN (PLACEHOLDER)
# ================================

@require_http_methods(["GET"])
def google_login(request):
    """Google ile giriş - Placeholder"""
    # TODO: Google OAuth2 implementasyonu
    messages.info(request, 'Google ile giriş özelliği yakında eklenecek!')
    return redirect('authentication:login')


@require_http_methods(["GET"])
def linkedin_login(request):
    """LinkedIn ile giriş - Placeholder"""
    # TODO: LinkedIn OAuth2 implementasyonu
    messages.info(request, 'LinkedIn ile giriş özelliği yakında eklenecek!')
    return redirect('authentication:login')


# ================================
# HELPER FUNCTIONS
# ================================

def format_phone_number(phone):
    """
    Telefon numarasını +905551234567 formatına çevir
    """
    # Sadece rakamları al
    phone = re.sub(r'\D', '', phone)
    
    # Başında 90 varsa +90 ekle
    if phone.startswith('90') and len(phone) == 12:
        return f"+{phone}"
    
    # Başında 0 varsa 90 ile değiştir
    if phone.startswith('0') and len(phone) == 11:
        return f"+9{phone}"
    
    # Başında hiçbiri yoksa +90 ekle
    if len(phone) == 10:
        return f"+90{phone}"
    
    return phone


def get_client_ip(request):
    """
    Kullanıcının IP adresini al
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
    
