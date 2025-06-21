from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Ana dashboard
    path('', views.dashboard_home, name='home'),
    
    # API endpoints
    path('api/stats/', views.get_dashboard_stats, name='get_stats'),
    path('api/chart-data/<str:period>/', views.get_chart_data, name='get_chart_data'),
    path('api/export/<str:format_type>/', views.export_dashboard_data, name='export_data'),
]
