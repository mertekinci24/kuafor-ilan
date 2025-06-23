from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import JobListing, JobCategory, JobApplication
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
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
        job_count=models.Count('id')
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
    
