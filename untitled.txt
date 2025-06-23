from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # Profile Views
    path('', views.profile_view, name='profile'),  # Kendi profili
    path('<int:user_id>/', views.profile_view, name='profile_detail'),  # Başka kullanıcı profili
    path('edit/', views.profile_edit_view, name='profile_edit'),  # Profil düzenleme
    
    # Job Seeker Specific
    path('applications/', views.my_applications_view, name='my_applications'),  # Başvurularım
    path('saved-jobs/', views.saved_jobs_view, name='saved_jobs'),  # Kaydedilenler
    
    # Business Specific  
    path('jobs/', views.my_jobs_view, name='my_jobs'),  # İlanlarım
    
    # Settings & Account
    path('settings/', views.settings_view, name='settings'),  # Ayarlar
    path('delete-account/', views.delete_account_view, name='delete_account'),  # Hesap silme
    
    # API Endpoints
    path('api/save-job/', views.save_job_api, name='save_job_api'),  # İş kaydetme
    path('api/upload-avatar/', views.upload_avatar_api, name='upload_avatar_api'),  # Avatar yükleme
    path('api/export-data/', views.export_profile_data, name='export_data'),  # Veri export
]
