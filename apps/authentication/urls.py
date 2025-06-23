from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Ana authentication URL'leri
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profil URL'leri
    path('profile/', views.profile_view, name='profile'),
    
    # API URL'leri - Mevcut
    path('api/check-email/', views.check_email_exists, name='check_email'),
    path('api/update-profile/', views.update_profile_api, name='update_profile_api'),
    
    # OTP API URL'leri - YENİ
    path('api/send-otp/', views.send_otp_api, name='send_otp'),
    path('api/verify-otp/', views.verify_otp_api, name='verify_otp'),
    path('api/check-phone/', views.check_phone_exists, name='check_phone'),
    
    # Sosyal medya URL'leri - YENİ
    path('google/', views.google_login, name='google_login'),
    path('linkedin/', views.linkedin_login, name='linkedin_login'),
]
