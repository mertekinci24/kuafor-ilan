from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_view, name='profile'),  # Kendi profili
    path('<int:user_id>/', views.profile_view, name='profile_detail'),  # Başka kullanıcı profili
    path('edit/', views.profile_edit_view, name='profile_edit'),  # Profil düzenleme
    path('applications/', views.my_applications_view, name='my_applications'),  # Başvurularım
    path('jobs/', views.my_jobs_view, name='my_jobs'),  # İlanlarım
]
