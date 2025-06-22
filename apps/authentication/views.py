from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model

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
    
