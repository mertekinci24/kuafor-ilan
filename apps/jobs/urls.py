from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Job listing and detail pages
    path('', views.jobs_list_view, name='list'),
    path('<int:job_id>/', views.job_detail_view, name='detail'),
    
    # Job actions
    path('<int:job_id>/apply/', views.apply_job_view, name='apply'),
    path('<int:job_id>/save/', views.save_job_view, name='save'),
    
    # Basic API endpoints
    path('api/search/', views.job_search_api, name='search_api'),
    path('api/categories/', views.categories_api, name='categories_api'),
    path('api/cities/', views.cities_api, name='cities_api'),
    path('api/my-applications/', views.my_applications_api, name='my_applications_api'),
    path('api/recommendations/', views.job_recommendations_api, name='recommendations_api'),
    
    # Advanced search endpoints
    path('api/search/advanced/', views.advanced_search_api, name='advanced_search_api'),
    path('api/search/suggestions/', views.search_suggestions_api, name='search_suggestions_api'),
    path('api/search/filters/', views.search_filters_api, name='search_filters_api'),
    path('api/search/analytics/', views.search_analytics_api, name='search_analytics_api'),
    path('api/search/log/', views.log_search_api, name='log_search_api'),
]
