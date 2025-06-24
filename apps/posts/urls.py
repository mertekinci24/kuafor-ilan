from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Post CRUD
    path('', views.posts_list_view, name='list'),
    path('create/', views.post_create_view, name='create'),
    path('<uuid:pk>/', views.post_detail_view, name='detail'),
    path('<uuid:pk>/edit/', views.post_edit_view, name='edit'),
    path('<uuid:pk>/delete/', views.post_delete_view, name='delete'),
    
    # Post Actions API
    path('api/like/', views.post_like_api, name='like_api'),
    path('api/save/', views.post_save_api, name='save_api'),
    path('api/share/', views.post_share_api, name='share_api'),
    
    # Comments API
    path('api/comments/', views.comments_api, name='comments_api'),
    path('api/comments/create/', views.comment_create_api, name='comment_create_api'),
    
    # Feed API
    path('api/feed/', views.feed_api, name='feed_api'),
]
