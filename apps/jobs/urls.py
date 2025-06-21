from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.jobs_list_view, name='list'),
    path('<int:job_id>/', views.job_detail_view, name='detail'),
    path('<int:job_id>/apply/', views.apply_job_view, name='apply'),
]
