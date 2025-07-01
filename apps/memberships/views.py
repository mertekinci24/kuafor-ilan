from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from .models import (
    SubscriptionPlan, 
    UserMembership, 
    MembershipPayment,
    MembershipUpgrade
)

def membership_plans(request):
    """Üyelik planlarını listele"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
    
    context = {
        'plans': plans,
        'current_user_plan': None
    }
    
    # Kullanıcının mevcut planını bul
    if request.user.is_authenticated:
        try:
            user_membership = UserMembership.objects.get(user=request.user)
            if user_membership.is_active():
                context['current_user_plan'] = user_membership.plan
        except UserMembership.DoesNotExist:
            pass
    
    return render(request, 'memberships/plans.html', context)


@login_required
def membership_dashboard(request):
    """Kullanıcının üyelik dashboard'u"""
    try:
        membership = UserMembership.objects.get(user=request.user)
    except UserMembership.DoesNotExist:
        # Kullanıcının üyeliği yok, ücretsiz plan oluştur
        free_plan = SubscriptionPlan.objects.get(plan_type='free')
        membership = UserMembership.objects.create(
            user=request.user,
            plan=free_plan,
            start_date=timezone.now(),
            end_date=timezone.now() + relativedelta(years=10),  # Ücretsiz plan hiç bitmesin
            status='active'
        )
    
    # Son ödemeler
    recent_payments = MembershipPayment.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Planlar arası karşılaştırma
    available_plans = SubscriptionPlan.objects.filter(
        is_active=True
    ).exclude(
        plan_type=membership.plan.plan_type
    ).order_by('sort_order', 'price')
    
    context = {
        'membership': membership,
        'recent_payments': recent_payments,
        'available_plans': available_plans,
        'days_remaining': membership.days_remaining(),
        'can_post_jobs': membership.can_post_job(),
        'remaining_job_posts': membership.remaining_job_posts()
    }
    
    return render(request, 'memberships/dashboard.html', context)


@login_required
def upgrade_plan(request, plan_id):
    """Plan yükseltme işlemi"""
    new_plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    try:
        current_membership = UserMembership.objects.get(user=request.user)
        current_plan = current_membership.plan
    except UserMembership.DoesNotExist:
        messages.error(request, 'Önce mevcut üyeliğinizi oluşturmanız gerekiyor.')
        return redirect('memberships:dashboard')
    
    # Aynı plan kontrolü
    if current_plan.plan_type == new_plan.plan_type:
        messages.warning(request, 'Zaten bu plana sahipsiniz.')
        return redirect('memberships:dashboard')
    
    # Düşürme kontrolü (opsiyonel)
    plan_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'enterprise': 3}
    if plan_hierarchy.get(new_plan.plan_type, 0) < plan_hierarchy.get(current_plan.plan_type, 0):
        messages.warning(request, 'Plan düşürme işlemi için lütfen destek ekibiyle iletişime geçin.')
        return redirect('memberships:dashboard')
    
    if request.method == 'POST':
        # Yükseltme talebini oluştur
        price_difference = new_plan.price - current_plan.price
        
        upgrade_request = MembershipUpgrade.objects.create(
            user=request.user,
            current_plan=current_plan,
            requested_plan=new_plan,
            price_difference=price_difference
        )
        
        # Ödeme sayfasına yönlendir
        return redirect('memberships:payment', upgrade_id=upgrade_request.id)
    
    # Plan karşılaştırması
    context = {
        'current_plan': current_plan,
        'new_plan': new_plan,
        'price_difference': new_plan.price - current_plan.price
    }
    
    return render(request, 'memberships/upgrade_confirm.html', context)


@login_required
def membership_payment(request, upgrade_id):
    """Üyelik ödeme sayfası"""
    upgrade = get_object_or_404(MembershipUpgrade, id=upgrade_id, user=request.user)
    
    if upgrade.status != 'pending':
        messages.error(request, 'Bu yükseltme talebi zaten işlenmiş.')
        return redirect('memberships:dashboard')
    
    if request.method == 'POST':
        # Ödeme işlemi burada yapılacak (iyzico entegrasyonu)
        # Şimdilik mock ödeme yapıyoruz
        
        try:
            with transaction.atomic():
                # Form'dan ödeme yöntemini al
                payment_method = request.POST.get('payment_method', 'credit_card')
                
                # Ödeme kaydı oluştur
                payment = MembershipPayment.objects.create(
                    user=request.user,
                    membership=request.user.membership,
                    plan=upgrade.requested_plan,
                    amount=upgrade.price_difference,
                    payment_method=payment_method,
                    status='completed',  # Mock ödeme başarılı
                    payment_date=timezone.now()
                )
                
                # Üyeliği güncelle
                current_membership = request.user.membership
                current_membership.plan = upgrade.requested_plan
                
                # Plan süresini uzat (aylık plan için)
                if upgrade.requested_plan.billing_cycle == 'monthly':
                    current_membership.end_date = current_membership.end_date + relativedelta(months=1)
                elif upgrade.requested_plan.billing_cycle == 'yearly':
                    current_membership.end_date = current_membership.end_date + relativedelta(years=1)
                
                current_membership.save()
                
                # Yükseltme talebini onayla
                upgrade.status = 'approved'
                upgrade.processed_at = timezone.now()
                upgrade.save()
                
                messages.success(request, f'Planınız başarıyla {upgrade.requested_plan.name} olarak yükseltildi!')
                return redirect('memberships:dashboard')
                
        except Exception as e:
            messages.error(request, 'Ödeme işlemi sırasında bir hata oluştu. Lütfen tekrar deneyin.')
    
    context = {
        'upgrade': upgrade,
        'amount': upgrade.price_difference
    }
    
    return render(request, 'memberships/payment.html', context)


@login_required
def cancel_membership(request):
    """Üyelik iptali"""
    try:
        membership = UserMembership.objects.get(user=request.user)
    except UserMembership.DoesNotExist:
        messages.error(request, 'Aktif üyeliğiniz bulunmuyor.')
        return redirect('memberships:dashboard')
    
    if request.method == 'POST':
        # Üyeliği iptal et (otomatik yenilemeyi kapat)
        membership.auto_renew = False
        membership.save()
        
        messages.success(request, 'Üyeliğinizin otomatik yenilenmesi durduruldu. Mevcut dönem sonuna kadar erişiminiz devam edecek.')
        return redirect('memberships:dashboard')
    
    return render(request, 'memberships/cancel_confirm.html', {'membership': membership})


def membership_ajax_check(request):
    """AJAX ile üyelik durumu kontrolü"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        membership = UserMembership.objects.get(user=request.user)
        data = {
            'plan_name': membership.plan.name,
            'plan_type': membership.plan.plan_type,
            'is_active': membership.is_active(),
            'days_remaining': membership.days_remaining(),
            'can_post_jobs': membership.can_post_job(),
            'remaining_job_posts': membership.remaining_job_posts(),
            'features': {
                'can_highlight_jobs': membership.plan.can_highlight_jobs,
                'can_feature_jobs': membership.plan.can_feature_jobs,
                'cv_pool_access': membership.plan.cv_pool_access,
                'priority_support': membership.plan.priority_support,
                'analytics_access': membership.plan.analytics_access,
            }
        }
        return JsonResponse(data)
        
    except UserMembership.DoesNotExist:
        return JsonResponse({'error': 'Membership not found'}, status=404)
        