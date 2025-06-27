from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication Pages
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    
    # OTP API Endpoints
    path('api/send-otp/', views.send_otp_api, name='send_otp_api'),
    path('api/verify-otp/', views.verify_otp_api, name='verify_otp_api'),
    
    # Social Authentication
    # path('google/', views.google_auth, name='google_auth'),
    # path('linkedin/', views.linkedin_auth, name='linkedin_auth'),
    # path('google/callback/', views.google_callback, name='google_callback'),
    # path('linkedin/callback/', views.linkedin_callback, name='linkedin_callback'),
    
    # Redirects
    path('profile/', views.profile_redirect, name='profile_redirect'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]
