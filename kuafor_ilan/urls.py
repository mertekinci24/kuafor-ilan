# kuafor_ilan/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.posts.views import home_page_view

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Ana sayfa - İş ilanları listesi
    path('', home_page_view, name='home'),

    # Authentication
    path('auth/', include('apps.authentication.urls')),

    # Ana uygulamalar
    path('posts/', include('apps.posts.urls')),
    path('jobs/', include('apps.jobs.urls')),
    path('profiles/', include('apps.profiles.urls')),
    path('dashboard/', include('apps.dashboard.urls')),

    # İletişim ve bildirim uygulamaları
    path('messages/', include('apps.messages.urls')),
    path('notifications/', include('apps.notifications.urls')),

    # Üyelik sistemi
    path('memberships/', include('apps.memberships.urls')),


    # WordPress bot koruması
    path('wp-admin/', RedirectView.as_view(url='/', permanent=False)),
    path('wp-login.php', RedirectView.as_view(url='/', permanent=False)),
    path('xmlrpc.php', RedirectView.as_view(url='/', permanent=False)),
]

# Static/Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    