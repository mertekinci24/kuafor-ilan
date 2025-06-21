from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView
from django.views.generic import TemplateView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', TemplateView.as_view(template_name='auth/register.html'), name='register'),
]
