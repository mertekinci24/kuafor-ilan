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
    
    # API URL'leri
    path('api/check-email/', views.check_email_exists, name='check_email'),
    path('api/update-profile/', views.update_profile_api, name='update_profile_api'),
]
