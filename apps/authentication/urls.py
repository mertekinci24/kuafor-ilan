from django.urls import path
from django.http import JsonResponse

def auth_root(request):
    return JsonResponse({
        'auth_endpoints': {
            'register': '/api/v1/auth/register/',
            'login': '/api/v1/auth/login/',
            'profile': '/api/v1/auth/profile/',
            'logout': '/api/v1/auth/logout/',
        },
        'status': 'Authentication API Active',
        'message': 'Kuaför İlan Authentication System'
    })

def register_view(request):
    return JsonResponse({
        'endpoint': 'register',
        'methods': ['POST'],
        'description': 'User registration endpoint',
        'fields': ['email', 'password', 'first_name', 'last_name', 'user_type']
    })

app_name = 'authentication'

urlpatterns = [
    path('', auth_root, name='auth_root'),
    path('register/', register_view, name='register'),
]
