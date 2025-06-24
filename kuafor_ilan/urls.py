from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.posts.views import posts_list_view

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Ana sayfa - post feed
    path('', posts_list_view, name='home'),
    
    # Authentication
    path('auth/', include('apps.authentication.urls')),
    
    # Ana uygulamalar
    path('posts/', include('apps.posts.urls')),
    path('jobs/', include('apps.jobs.urls')),
    path('profiles/', include('apps.profiles.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    
    # WordPress bot koruması
    path('wp-admin/', RedirectView.as_view(url='/', permanent=False)),
    path('wp-login.php', RedirectView.as_view(url='/', permanent=False)),
    path('xmlrpc.php', RedirectView.as_view(url='/', permanent=False)),
]

# Static/Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
