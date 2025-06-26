from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Ana bildirimler sayfası
    path('', views.notifications_list, name='list'),
    
    # Bildirim detayı
    path('<uuid:notification_id>/', views.notification_detail, name='detail'),
    
    # Bildirim işlemleri
    path('<uuid:notification_id>/read/', views.mark_as_read, name='mark_read'),
    path('<uuid:notification_id>/delete/', views.delete_notification, name='delete'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('delete-selected/', views.delete_selected, name='delete_selected'),
    
    # Ayarlar
    path('settings/', views.notification_settings, name='settings'),
    
    # API endpoints
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
    path('api/recent/', views.get_recent_notifications, name='recent'),
    path('api/search/', views.search_notifications, name='search'),
    path('api/preferences/', views.notification_preferences_api, name='preferences_api'),
    
    # Test ve webhook
    path('api/test/', views.test_notification, name='test'),
    path('webhook/', views.webhook_notification, name='webhook'),
]

