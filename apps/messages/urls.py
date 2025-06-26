from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    # Ana mesajlar sayfası
    path('', views.messages_list, name='list'),
    
    # Sohbet detayı
    path('<uuid:conversation_id>/', views.conversation_detail, name='detail'),
    
    # Yeni sohbet başlat
    path('start/<int:user_id>/', views.start_conversation, name='start'),
    
    # Mesaj gönderme
    path('<uuid:conversation_id>/send/', views.send_message, name='send'),
    
    # Dosya yükleme
    path('<uuid:conversation_id>/upload/', views.upload_message_file, name='upload_file'),
    
    # Kullanıcı engelleme
    path('block/<int:user_id>/', views.block_user, name='block'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock'),
    path('blocked/', views.blocked_users_list, name='blocked_list'),
    
    # Mesaj işlemleri
    path('message/<uuid:message_id>/delete/', views.delete_message, name='delete_message'),
    path('message/<uuid:message_id>/report/', views.report_message, name='report_message'),
    
    # Sohbet işlemleri
    path('<uuid:conversation_id>/mark-read/', views.mark_conversation_read, name='mark_read'),
    
    # API endpoints
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
    path('api/search/', views.search_conversations, name='search'),
    path('api/<uuid:conversation_id>/messages/', views.get_conversation_messages, name='messages_api'),
]

