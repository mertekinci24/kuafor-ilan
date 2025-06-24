from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.http import HttpResponseNotFound

def home_view(request):
    """Ana sayfa view'ı - Giriş yapmış kullanıcılar da anasayfayı görebilir"""
    return render(request, 'home.html')

def block_bots(request):
    """Bot isteklerini engelle"""
    return HttpResponseNotFound("Not Found")

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Ana sayfa
    path('', home_view, name='home'),
    
    # Authentication URL'leri
    path('auth/', include('apps.authentication.urls')),
    
    # Dashboard URL'leri
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Jobs URL'leri
    path('jobs/', include('apps.jobs.urls')),
    
    # Profiles URL'leri - BU SATIRI EKLEYİN
    path('profiles/', include('apps.profiles.urls')),

    path('posts/', include('apps.posts.urls')),
    
    # WordPress bot koruması
    re_path(r'^wp-.*', block_bots),
    re_path(r'^wordpress.*', block_bots),
    re_path(r'^.*wp-admin.*', block_bots),
    re_path(r'^.*wp-login.*', block_bots),
    re_path(r'^.*wp-content.*', block_bots),
    re_path(r'^.*wp-includes.*', block_bots),
    re_path(r'^xmlrpc\.php$', block_bots),
    re_path(r'^.*\.php$', block_bots),
    re_path(r'^phpmyadmin.*', block_bots),
    re_path(r'^admin\.php$', block_bots),
    re_path(r'^administrator.*', block_bots),
    re_path(r'^.*\.asp$', block_bots),
    re_path(r'^.*\.aspx$', block_bots),
]

# Development için media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
