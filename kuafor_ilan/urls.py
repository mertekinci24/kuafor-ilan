from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def home_view(request):
    """Ana sayfa view'ı"""
    return render(request, 'home.html')

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Ana sayfa
    path('', home_view, name='home'),
    
    # Dashboard URL'leri
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Authentication geçici kapalı - migration sorunu
    # path('auth/', include('apps.authentication.urls')),
]

# Development için media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
