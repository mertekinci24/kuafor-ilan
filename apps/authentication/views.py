from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.http import JsonResponse
import json

User = get_user_model()


@csrf_protect
def login_view(request):
    """Giriş sayfası"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        email = request.POST.get('username')  # email field'ı username olarak geliyor
        password = request.POST.get('password')
        
        # E-posta ile giriş
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Giriş bilgileriniz hatalı. Lütfen tekrar deneyin.')
    
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
            
            # E-posta kontrolü
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Bu e-posta adresi zaten kullanılıyor.')
                return render(request, 'auth/register.html')
            
            # Kullanıcı oluştur
            user = User.objects.create_user(
                username=email,  # username olarak email kullan
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type
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
                if hasattr(user, field):
                    setattr(user, field, value)
                    updated_fields.append(field)
        
        # E-posta güncelleme (özel kontrol)
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if new_email != user.email:
                # E-posta kullanımda mı kontrol et
                if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Bu e-posta adresi zaten kullanılıyor.'
                    }, status=400)
                
                user.email = new_email
                user.username = new_email  # Username da email olduğu için güncelle
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
        
