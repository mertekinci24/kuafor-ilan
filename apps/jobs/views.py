from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import JobListing, JobCategory, JobApplication
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

def jobs_list_view(request):
    """İş ilanları listesi sayfası"""
    # Filtreleme parametreleri
    category_id = request.GET.get('category')
    city = request.GET.get('city')
    search = request.GET.get('search')
    salary_min = request.GET.get('salary_min')
    salary_max = request.GET.get('salary_max')
    
    # Tüm aktif iş ilanları
    jobs = JobListing.objects.filter(status='active').order_by('-created_at')
    
    # Filtreleme işlemleri
    if category_id:
        jobs = jobs.filter(category_id=category_id)
    
    if city:
        jobs = jobs.filter(city__icontains=city)
    
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    if salary_min:
        jobs = jobs.filter(salary_min__gte=salary_min)
    
    if salary_max:
        jobs = jobs.filter(salary_max__lte=salary_max)
    
    # Sayfalama
    paginator = Paginator(jobs, 10)  # Her sayfada 10 ilan
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Kategoriler (filtre için)
    categories = JobCategory.objects.all()
    
    # Şehir listesi (mevcut ilanlardan)
    cities = JobListing.objects.filter(status='active').values_list('city', flat=True).distinct()
    
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
    job.save()
    
    # Benzer ilanlar (aynı kategori ve şehir)
    similar_jobs = JobListing.objects.filter(
        category=job.category,
        city=job.city,
        status='active'
    ).exclude(id=job.id)[:3]
    
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
def apply_job_view(request, job_id):
    """İş ilanına başvuru"""
    if request.method == 'POST':
        job = get_object_or_404(JobListing, id=job_id, status='active')
        cover_letter = request.POST.get('cover_letter', '')
        
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
        
        # Yeni başvuru oluştur
        application = JobApplication.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Başvurunuz başarıyla gönderildi!'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Geçersiz istek!'
    })
  
