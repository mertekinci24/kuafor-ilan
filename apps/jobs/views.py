from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Min, Max, Sum
from .models import JobListing, JobCategory, JobApplication
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.db import models
import json
import logging

logger = logging.getLogger(__name__)

def jobs_list_view(request):
    """İş ilanları listesi sayfası"""
    # Filtreleme parametreleri
    category_id = request.GET.get('category')
    city = request.GET.get('city')
    search = request.GET.get('search')
    salary_min = request.GET.get('salary_min')
    salary_max = request.GET.get('salary_max')
    
    # Tüm aktif iş ilanları
    jobs = JobListing.objects.filter(status='active').select_related('business', 'category').order_by('-created_at')
    
    # Filtreleme işlemleri
    if category_id:
        jobs = jobs.filter(category_id=category_id)
    
    if city:
        jobs = jobs.filter(city__icontains=city)
    
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(category__name__icontains=search)
        )
    
    if salary_min:
        try:
            jobs = jobs.filter(salary_min__gte=int(salary_min))
        except ValueError:
            pass
    
    if salary_max:
        try:
            jobs = jobs.filter(salary_max__lte=int(salary_max))
        except ValueError:
            pass
    
    # Sayfalama
    paginator = Paginator(jobs, 10)  # Her sayfada 10 ilan
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Kategoriler (filtre için)
    categories = JobCategory.objects.all().order_by('name')
    
    # Şehir listesi (mevcut ilanlardan)
    cities = JobListing.objects.filter(status='active').values_list('city', flat=True).distinct().order_by('city')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'cities': cities,
        'current_filters': {
            'category': category_id,
            'city': city,
            'search': search,
            'salary_min': salary_min,
            'salary_max': salary_max,
        }
    }
    
    return render(request, 'jobs/jobs_list.html', context)

def job_detail_view(request, job_id):
    """İş ilanı detay sayfası"""
    job = get_object_or_404(JobListing, id=job_id, status='active')
    
    # Görüntülenme sayısını artır
    job.views_count += 1
    job.save(update_fields=['views_count'])
    
    # Benzer ilanlar (aynı kategori ve şehir)
    similar_jobs = JobListing.objects.filter(
        category=job.category,
        city=job.city,
        status='active'
    ).exclude(id=job.id).select_related('business', 'category')[:3]
    
    # Kullanıcı başvuru durumu
    user_applied = False
    if request.user.is_authenticated:
        user_applied = JobApplication.objects.filter(
            job=job,
            applicant=request.user
        ).exists()
    
    context = {
        'job': job,
        'similar_jobs': similar_jobs,
        'user_applied': user_applied,
    }
    
    return render(request, 'jobs/job_detail.html', context)

@login_required
@require_http_methods(["POST"])
def apply_job_view(request, job_id):
    """İş ilanına başvuru"""
    try:
        job = get_object_or_404(JobListing, id=job_id, status='active')
        
        # İş veren kendi ilanına başvuru yapamaz
        if job.business == request.user:
            return JsonResponse({
                'success': False,
                'message': 'Kendi ilanınıza başvuru yapamazsınız!'
            })
        
        # İş arayan olmayan kullanıcılar başvuru yapamaz
        if request.user.user_type != 'jobseeker':
            return JsonResponse({
                'success': False,
                'message': 'Sadece iş arayanlar başvuru yapabilir!'
            })
        
        # Daha önce başvuru kontrolü
        existing_application = JobApplication.objects.filter(
            job=job,
            applicant=request.user
        ).first()
        
        if existing_application:
            return JsonResponse({
                'success': False,
                'message': 'Bu ilana zaten başvurdunuz!'
            })
        
        # Ön yazıyı al
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            cover_letter = data.get('cover_letter', '')
        else:
            cover_letter = request.POST.get('cover_letter', '')
        
        # Yeni başvuru oluştur
        application = JobApplication.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter
        )
        
        # İş arayan profilinin başvuru sayısını artır
        if hasattr(request.user, 'jobseeker_profile'):
            profile = request.user.jobseeker_profile
            profile.total_applications += 1
            profile.save(update_fields=['total_applications'])
        
        logger.info(f"Job application created: {request.user.email} applied to {job.title}")
        
        return JsonResponse({
            'success': True,
            'message': 'Başvurunuz başarıyla gönderildi!'
        })
        
    except Exception as e:
        logger.error(f"Job application error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Başvuru sırasında bir hata oluştu. Lütfen tekrar deneyin.'
        })

@login_required
@require_http_methods(["POST"])
def save_job_view(request, job_id):
    """İş ilanını kaydet/kaldır"""
    try:
        from apps.profiles.models import SavedJob
        
        if request.user.user_type != 'jobseeker':
            return JsonResponse({
                'success': False,
                'message': 'Bu işlem sadece iş arayanlar için geçerlidir.'
            })
        
        job = get_object_or_404(JobListing, id=job_id, status='active')
        
        saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
        
        if created:
            return JsonResponse({
                'success': True,
                'saved': True,
                'message': 'İlan kaydedildi!'
            })
        else:
            saved_job.delete()
            return JsonResponse({
                'success': True,
                'saved': False,
                'message': 'İlan kaydetme kaldırıldı!'
            })
            
    except Exception as e:
        logger.error(f"Save job error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Bir hata oluştu.'
        })

def job_search_api(request):
    """İş arama API"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    city = request.GET.get('city', '')
    
    jobs = JobListing.objects.filter(status='active')
    
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    if category:
        jobs = jobs.filter(category_id=category)
    
    if city:
        jobs = jobs.filter(city__icontains=city)
    
    jobs = jobs.select_related('business', 'category')[:10]
    
    results = []
    for job in jobs:
        results.append({
            'id': job.id,
            'title': job.title,
            'company': job.business.get_full_name(),
            'city': job.city,
            'category': job.category.name,
            'salary_range': f"₺{job.salary_min}-{job.salary_max}" if job.salary_min and job.salary_max else "Maaş görüşülür",
            'is_urgent': job.is_urgent,
            'created_at': job.created_at.isoformat(),
        })
    
    return JsonResponse({
        'success': True,
        'results': results,
        'count': len(results)
    })

def categories_api(request):
    """Kategoriler API"""
    categories = JobCategory.objects.all().order_by('name')
    
    results = []
    for category in categories:
        job_count = JobListing.objects.filter(category=category, status='active').count()
        results.append({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'job_count': job_count
        })
    
    return JsonResponse({
        'success': True,
        'categories': results
    })

def cities_api(request):
    """Şehirler API"""
    cities = JobListing.objects.filter(
        status='active'
    ).values('city').annotate(
        job_count=Count('id')
    ).order_by('city')
    
    results = []
    for city_data in cities:
        results.append({
            'name': city_data['city'],
            'job_count': city_data['job_count']
        })
    
    return JsonResponse({
        'success': True,
        'cities': results
    })

@login_required
def my_applications_api(request):
    """Kullanıcının başvuruları API"""
    if request.user.user_type != 'jobseeker':
        return JsonResponse({
            'success': False,
            'message': 'Bu API sadece iş arayanlar için geçerlidir.'
        })
    
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__business', 'job__category').order_by('-created_at')[:10]
    
    results = []
    for app in applications:
        results.append({
            'id': app.id,
            'job_title': app.job.title,
            'company': app.job.business.get_full_name(),
            'status': app.status,
            'applied_at': app.created_at.isoformat(),
            'job_url': f"/jobs/{app.job.id}/",
        })
    
    return JsonResponse({
        'success': True,
        'applications': results
    })

@login_required
def job_recommendations_api(request):
    """İş önerileri API"""
    if request.user.user_type != 'jobseeker':
        return JsonResponse({
            'success': False,
            'message': 'Bu API sadece iş arayanlar için geçerlidir.'
        })
    
    # Basit öneri algoritması
    user_applications = JobApplication.objects.filter(
        applicant=request.user
    ).values_list('job__category_id', flat=True)
    
    # Kullanıcının başvurduğu kategorilerden ilanlar öner
    if user_applications:
        jobs = JobListing.objects.filter(
            category_id__in=user_applications,
            status='active'
        ).exclude(
            id__in=JobApplication.objects.filter(
                applicant=request.user
            ).values_list('job_id', flat=True)
        ).select_related('business', 'category').order_by('-created_at')[:5]
    else:
        # Yeni kullanıcılar için en son ilanları öner
        jobs = JobListing.objects.filter(
            status='active'
        ).select_related('business', 'category').order_by('-created_at')[:5]
    
    results = []
    for job in jobs:
        results.append({
            'id': job.id,
            'title': job.title,
            'company': job.business.get_full_name(),
            'city': job.city,
            'category': job.category.name,
            'is_urgent': job.is_urgent,
            'created_at': job.created_at.isoformat(),
        })
    
    return JsonResponse({
        'success': True,
        'recommendations': results
    })

# ======================== ADVANCED SEARCH SYSTEM ========================

def advanced_search_api(request):
    """Advanced search with autocomplete and suggestions"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    city = request.GET.get('city', '')
    salary_min = request.GET.get('salary_min', '')
    salary_max = request.GET.get('salary_max', '')
    sort_by = request.GET.get('sort', 'newest')
    limit = int(request.GET.get('limit', 10))
    
    # Cache key for performance
    cache_key = f"search_{hash(str(request.GET))}"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return JsonResponse(cached_result)
    
    # Base queryset
    jobs = JobListing.objects.filter(status='active').select_related('business', 'category')
    
    # Search query
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(business__first_name__icontains=query) |
            Q(business__last_name__icontains=query)
        )
    
    # Filters
    if category:
        jobs = jobs.filter(category_id=category)
    
    if city:
        jobs = jobs.filter(city__icontains=city)
    
    if salary_min:
        try:
            jobs = jobs.filter(
                Q(salary_min__gte=int(salary_min)) | 
                Q(salary_max__gte=int(salary_min))
            )
        except ValueError:
            pass
    
    if salary_max:
        try:
            jobs = jobs.filter(
                Q(salary_max__lte=int(salary_max)) | 
                Q(salary_min__lte=int(salary_max))
            )
        except ValueError:
            pass
    
    # Sorting
    if sort_by == 'newest':
        jobs = jobs.order_by('-created_at')
    elif sort_by == 'oldest':
        jobs = jobs.order_by('created_at')
    elif sort_by == 'salary_high':
        jobs = jobs.order_by('-salary_max', '-salary_min')
    elif sort_by == 'salary_low':
        jobs = jobs.order_by('salary_min', 'salary_max')
    elif sort_by == 'popular':
        jobs = jobs.order_by('-views_count')
    
    # Limit results
    jobs = jobs[:limit]
    
    # Build results
    results = []
    for job in jobs:
        salary_display = "Maaş görüşülür"
        if job.salary_min and job.salary_max:
            salary_display = f"₺{job.salary_min:,} - ₺{job.salary_max:,}"
        elif job.salary_min:
            salary_display = f"₺{job.salary_min:,}+"
        
        results.append({
            'id': job.id,
            'title': job.title,
            'company': job.business.get_full_name() or job.business.email,
            'city': job.city,
            'district': job.district,
            'category': {
                'id': job.category.id,
                'name': job.category.name
            },
            'salary_display': salary_display,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'is_urgent': job.is_urgent,
            'views_count': job.views_count,
            'created_at': job.created_at.isoformat(),
            'url': f'/jobs/{job.id}/',
            'description_preview': job.description[:150] + '...' if len(job.description) > 150 else job.description
        })
    
    response_data = {
        'success': True,
        'results': results,
        'count': len(results),
        'query': query,
        'filters_applied': {
            'category': category,
            'city': city,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'sort_by': sort_by
        }
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, response_data, 300)
    
    return JsonResponse(response_data)

def search_suggestions_api(request):
    """Search autocomplete suggestions"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    cache_key = f"suggestions_{query}"
    cached_suggestions = cache.get(cache_key)
    
    if cached_suggestions:
        return JsonResponse({'suggestions': cached_suggestions})
    
    suggestions = []
    
    # Job titles
    job_titles = JobListing.objects.filter(
        title__icontains=query,
        status='active'
    ).values_list('title', flat=True).distinct()[:5]
    
    for title in job_titles:
        suggestions.append({
            'type': 'job_title',
            'text': title,
            'display': title,
            'icon': 'briefcase'
        })
    
    # Categories
    categories = JobCategory.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True)[:3]
    
    for category in categories:
        suggestions.append({
            'type': 'category',
            'text': category,
            'display': f"Kategori: {category}",
            'icon': 'tag'
        })
    
    # Cities
    cities = JobListing.objects.filter(
        city__icontains=query,
        status='active'
    ).values_list('city', flat=True).distinct()[:3]
    
    for city in cities:
        suggestions.append({
            'type': 'city',
            'text': city,
            'display': f"Şehir: {city}",
            'icon': 'map-marker-alt'
        })
    
    # Companies
    companies = JobListing.objects.filter(
        Q(business__first_name__icontains=query) |
        Q(business__last_name__icontains=query),
        status='active'
    ).select_related('business').distinct()[:3]
    
    for job in companies:
        company_name = job.business.get_full_name() or job.business.email
        suggestions.append({
            'type': 'company',
            'text': company_name,
            'display': f"Şirket: {company_name}",
            'icon': 'building'
        })
    
    # Cache for 10 minutes
    cache.set(cache_key, suggestions, 600)
    
    return JsonResponse({'suggestions': suggestions})

def search_filters_api(request):
    """Get available filters for search"""
    cache_key = "search_filters"
    cached_filters = cache.get(cache_key)
    
    if cached_filters:
        return JsonResponse(cached_filters)
    
    # Categories with job counts
    categories = JobCategory.objects.annotate(
        job_count=Count('joblisting', filter=Q(joblisting__status='active'))
    ).filter(job_count__gt=0).order_by('name')
    
    # Cities with job counts
    cities = JobListing.objects.filter(
        status='active'
    ).values('city').annotate(
        job_count=Count('id')
    ).order_by('city')
    
    # Salary ranges
    salary_stats = JobListing.objects.filter(
        status='active',
        salary_min__isnull=False,
        salary_max__isnull=False
    ).aggregate(
        min_salary=Min('salary_min'),
        max_salary=Max('salary_max'),
        avg_salary=Avg('salary_min')
    )
    
    filters_data = {
        'success': True,
        'categories': [
            {
                'id': cat.id,
                'name': cat.name,
                'job_count': cat.job_count
            } for cat in categories
        ],
        'cities': [
            {
                'name': city['city'],
                'job_count': city['job_count']
            } for city in cities
        ],
        'salary_ranges': [
            {'label': '0 - 5.000 TL', 'min': 0, 'max': 5000},
            {'label': '5.000 - 10.000 TL', 'min': 5000, 'max': 10000},
            {'label': '10.000 - 20.000 TL', 'min': 10000, 'max': 20000},
            {'label': '20.000+ TL', 'min': 20000, 'max': None},
        ],
        'salary_stats': salary_stats,
        'sort_options': [
            {'value': 'newest', 'label': 'En Yeni'},
            {'value': 'oldest', 'label': 'En Eski'},
            {'value': 'salary_high', 'label': 'Maaş (Yüksek→Düşük)'},
            {'value': 'salary_low', 'label': 'Maaş (Düşük→Yüksek)'},
            {'value': 'popular', 'label': 'En Çok Görüntülenen'},
        ]
    }
    
    # Cache for 1 hour
    cache.set(cache_key, filters_data, 3600)
    
    return JsonResponse(filters_data)

def search_analytics_api(request):
    """Search analytics and trending"""
    cache_key = "search_analytics"
    cached_analytics = cache.get(cache_key)
    
    if cached_analytics:
        return JsonResponse(cached_analytics)
    
    # Most popular categories
    popular_categories = JobCategory.objects.annotate(
        job_count=Count('joblisting', filter=Q(joblisting__status='active')),
        total_views=Sum('joblisting__views_count', filter=Q(joblisting__status='active'))
    ).filter(job_count__gt=0).order_by('-total_views')[:5]
    
    # Trending cities
    trending_cities = JobListing.objects.filter(
        status='active',
        created_at__gte=timezone.now() - timedelta(days=7)
    ).values('city').annotate(
        new_jobs=Count('id')
    ).order_by('-new_jobs')[:5]
    
    # Recent searches (would need to implement search logging)
    trending_searches = JobListing.objects.filter(
        status='active',
        views_count__gt=10
    ).order_by('-views_count')[:10].values_list('title', flat=True)
    
    analytics_data = {
        'success': True,
        'popular_categories': [
            {
                'name': cat.name,
                'job_count': cat.job_count or 0,
                'total_views': cat.total_views or 0
            } for cat in popular_categories
        ],
        'trending_cities': [
            {
                'name': city['city'],
                'new_jobs': city['new_jobs']
            } for city in trending_cities
        ],
        'trending_searches': list(trending_searches),
        'total_active_jobs': JobListing.objects.filter(status='active').count(),
        'total_categories': JobCategory.objects.count(),
    }
    
    # Cache for 1 hour
    cache.set(cache_key, analytics_data, 3600)
    
    return JsonResponse(analytics_data)

@require_http_methods(["POST"])
def log_search_api(request):
    """Log search queries for analytics"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        filters = data.get('filters', {})
        results_count = data.get('results_count', 0)
        
        if query:
            logger.info(f"Search logged: '{query}' - {results_count} results")
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        logger.error(f"Search logging error: {str(e)}")
        return JsonResponse({'success': False})
    