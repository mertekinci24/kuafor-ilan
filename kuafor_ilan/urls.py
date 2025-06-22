from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    # path('auth/', include('apps.authentication.urls')),  # Kapatın
    path('dashboard/', include('apps.dashboard.urls')),
    # path('profile/', include('apps.profiles.urls')),     # Kapatın
    # path('jobs/', include('apps.jobs.urls')),           # Kapatın
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
