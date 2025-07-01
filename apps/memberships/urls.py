from django.urls import path
from . import views

app_name = 'memberships'

urlpatterns = [
    # Üyelik planları
    path('plans/', views.membership_plans, name='plans'),
    
    # Kullanıcı üyelik yönetimi
    path('dashboard/', views.membership_dashboard, name='dashboard'),
    path('upgrade/<int:plan_id>/', views.upgrade_plan, name='upgrade'),
    path('payment/<int:upgrade_id>/', views.membership_payment, name='payment'),
    path('cancel/', views.cancel_membership, name='cancel'),
    
    # AJAX endpoints
    path('api/check/', views.membership_ajax_check, name='ajax_check'),
]