from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json

from .models import CustomUser, JobSeekerProfile, BusinessProfile
from .forms import LoginForm, RegisterForm


@csrf_protect
def login_view(request):
    """Giriş sayfası"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # E-posta veya telefon ile giriş
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Remember me functionality
                if remember_me:
                    request.session.set_expiry(86400 * 30)  # 30 gün
                else:
                    request.session.set_expiry(0)  # Browser kapanınca silinir
                
                # Son giriş IP'sini kaydet
                user.last_login_ip = get_client_ip(request)
                user.save()
                
                # Dashboard'a yönlendir
                next_url = request.GET.get('next', '/dashboard/')
                return redirect(next_url)
            else:
                messages.error(request, 'Giriş bilgileriniz hatalı. Lütfen tekrar deneyin.')
                return redirect('/auth/login/?error=1')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@csrf_protect
def register_view(request):
    """Kayıt sayfası"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Temel kullanıcı bilgileri
            user_type = data.get('user_type', 'jobseeker')
            email = data.get('email')
            password = data.get('password')
            selected_plan = data.get('selected_plan', 'free')
            
            # E-posta kontrolü
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Bu e-posta adresi zaten kullanılıyor.')
                return render(request, 'auth/register.html')
            
            # Kullanıcı oluştur
            if user_type == 'jobseeker':
                user = create_jobseeker_user(data, selected_plan)
            else:
                user = create_business_user(data, selected_plan)
            
            if user:
                # Otomatik giriş yap
                user = authenticate(request, username=email, password=password)
                login(request, user)
                
                messages.success(request, 'Hesabınız başarıyla oluşturuldu!')
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Hesap oluşturulurken bir hata oluştu.')
                
        except Exception as e:
            messages.error(request, f'Bir hata oluştu: {str(e)}')
    
    return render(request, 'auth/register.html')


def create_jobseeker_user(data, plan):
    """İş arayan kullanıcı oluştur"""
    try:
        # Kullanıcı oluştur
        user = CustomUser.objects.create_user(
            username=data.get('email'),
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone', ''),
            user_type='jobseeker',
            current_plan=plan
        )
        
        # Plan süresi ayarla
        if plan != 'free':
            user.plan_start_date = timezone.now()
            user.plan_end_date = timezone.now() + timedelta(days=30)
        
        user.save()
        
        # JobSeeker profili oluştur
        JobSeekerProfile.objects.create(
            user=user,
            city=data.get('city', ''),
            experience_years=data.get('experience_years', 'beginner'),
            skills=[],
            bio='',
        )
        
        return user
        
    except Exception as e:
        print(f"JobSeeker oluşturma hatası: {e}")
        return None


def create_business_user(data, plan):
    """İş veren kullanıcı oluştur"""
    try:
        # Kullanıcı oluştur
        user = CustomUser.objects.create_user(
            username=data.get('email'),
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('contact_person', '').split()[0] if data.get('contact_person') else '',
            last_name=' '.join(data.get('contact_person', '').split()[1:]) if data.get('contact_person') else '',
            phone=data.get('phone', ''),
            user_type='business',
            current_plan=plan
        )
        
        # Plan süresi ayarla
        if plan != 'free':
            user.plan_start_date = timezone.now()
            user.plan_end_date = timezone.now() + timedelta(days=30)
        
        user.save()
        
        # Business profili oluştur
        BusinessProfile.objects.create(
            user=user,
            company_name=data.get('company_name', ''),
            company_size='1-5',
            establishment_year=int(data.get('establishment_year', timezone.now().year)),
            city=data.get('city', ''),
            address='',
            contact_person=data.get('contact_person', ''),
            contact_phone=data.get('phone', ''),
        )
        
        return user
        
    except Exception as e:
        print(f"Business oluşturma hatası: {e}")
        return None


@login_required
def logout_view(request):
    """Çıkış"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('/')


@login_required
def profile_view(request):
    """Profil sayfası"""
    user = request.user
    
    context = {
        'user': user,
    }
    
    if user.user_type == 'jobseeker':
        try:
            profile = user.jobseeker_profile
            context['profile'] = profile
        except JobSeekerProfile.DoesNotExist:
            # Profil yoksa oluştur
            profile = JobSeekerProfile.objects.create(user=user, city='', experience_years='beginner')
            context['profile'] = profile
    else:
        try:
            profile = user.business_profile
            context['profile'] = profile
        except BusinessProfile.DoesNotExist:
            # Profil yoksa oluştur
            profile = BusinessProfile.objects.create(
                user=user,
                company_name='',
                establishment_year=timezone.now().year,
                city='',
                address='',
                contact_person=user.get_full_name(),
                contact_phone=user.phone
            )
            context['profile'] = profile
    
    return render(request, 'auth/profile.html', context)


def get_client_ip(request):
    """Kullanıcının IP adresini al"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# API Views
def check_email_exists(request):
    """E-posta kontrolü (AJAX)"""
    if request.method == 'POST':
        email = request.POST.get('email')
        exists = CustomUser.objects.filter(email=email).exists()
        return JsonResponse({'exists': exists})
    
    return JsonResponse({'error': 'Invalid request'})


@login_required
def update_profile_api(request):
    """Profil güncelleme API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            
            # Temel kullanıcı bilgilerini güncelle
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.phone = data.get('phone', user.phone)
            user.save()
            
            # Profil bilgilerini güncelle
            if user.user_type == 'jobseeker':
                profile = user.jobseeker_profile
                profile.city = data.get('city', profile.city)
                profile.experience_years = data.get('experience_years', profile.experience_years)
                profile.bio = data.get('bio', profile.bio)
                profile.save()
            else:
                profile = user.business_profile
                profile.company_name = data.get('company_name', profile.company_name)
                profile.city = data.get('city', profile.city)
                profile.address = data.get('address', profile.address)
                profile.save()
            
            return JsonResponse({'success': True, 'message': 'Profil güncellendi'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'error': 'Invalid request'})
    
