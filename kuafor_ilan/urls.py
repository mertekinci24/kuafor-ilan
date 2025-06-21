from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import render

def api_root(request):
    return JsonResponse({
        'message': 'Kuaför İlan API',
        'version': '1.0.0',
        'status': 'active',
        'website': 'https://kuaforilan.com',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'profiles': '/api/v1/profiles/',
            'jobs': '/api/v1/jobs/',
            'admin': '/admin/',
        }
    })

def home_view(request):
    """Ana sayfa view'ı"""
    return render(request, 'home.html')

urlpatterns = [
    path('', home_view, name='home'),
    path('api/', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('auth/', include('apps.authentication.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('jobs/', include('apps.jobs.urls')),
    path('profile/', include('apps.profiles.urls')),  # Bu satır yeni
    path('api/v1/auth/', include('apps.authentication.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "Kuaför İlan Admin"
admin.site.site_title = "Kuaför İlan Admin Portal"
admin.site.index_title = "Kuaför İlan Yönetim Paneli"

