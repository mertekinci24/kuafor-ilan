from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

def test_view(request):
    return JsonResponse({
        'status': 'success',
        'message': 'Django is working!',
        'app': 'Kuaför İlan'
    })

urlpatterns = [
    path('', test_view, name='home'),
    path('admin/', admin.site.urls),
]
