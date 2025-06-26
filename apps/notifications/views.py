from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from .models import Notification, NotificationType, UserNotificationSettings
from .services import NotificationService

logger = logging.getLogger(__name__)


@login_required
def notifications_list(request):
    """Bildirimler ana sayfası"""
    user = request.user
    
    # Filtreleme parametreleri
    filter_type = request.GET.get('type', 'all')
    is_read = request.GET.get('read')
    
    # Temel sorgu
    notifications = Notification.objects.filter(
        recipient=user
    ).select_related('notification_type').order_by('-created_at')
    
    # Filtreleme
    if filter_type != 'all':
        notifications = notifications.filter(notification_type__code=filter_type)
    
    if is_read == 'true':
        notifications = notifications.filter(is_read=True)
    elif is_read == 'false':
        notifications = notifications.filter(is_read=False)
    
    # Sayfalama
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    # İstatistikler
    stats = {
        'total': Notification.objects.filter(recipient=user).count(),
        'unread': Notification.objects.filter(recipient=user, is_read=False).count(),
        'today': Notification.objects.filter(
            recipient=user,
            created_at__date=timezone.now().date()
        ).count(),
    }
    
    # Bildirim türleri (filtre için)
    notification_types = NotificationType.objects.filter(
        is_active=True
    ).annotate(
        notification_count=Count('notification', filter=Q(notification__recipient=user))
    ).filter(notification_count__gt=0)
    
    context = {
        'notifications': notifications_page.object_list,
        'notifications_page': notifications_page,
        'stats': stats,
        'notification_types': notification_types,
        'current_filter': filter_type,
        'current_read_filter': is_read,
    }
    
    return render(request, 'notifications/list.html', context)


@login_required
def notification_detail(request, notification_id):
    """Bildirim detayı"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )
    
    # Bildirimi okundu olarak işaretle
    if not notification.is_read:
        notification.mark_as_read()
    
    # Eğer action_url varsa oraya yönlendir
    if notification.action_url:
        return redirect(notification.action_url)
    
    context = {
        'notification': notification,
    }
    
    return render(request, 'notifications/detail.html', context)


@login_required
@require_http_methods(["POST"])
def mark_as_read(request, notification_id):
    """Bildirimi okundu olarak işaretle"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )
    
    notification.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'message': 'Bildirim okundu olarak işaretlendi.'
    })


@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """Tüm bildirimleri okundu olarak işaretle"""
    updated_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({
        'success': True,
        'message': f'{updated_count} bildirim okundu olarak işaretlendi.',
        'updated_count': updated_count
    })


@login_required
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    """Bildirimi sil"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )
    
    notification.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Bildirim silindi.'
    })


@login_required
@require_http_methods(["POST"])
def delete_selected(request):
    """Seçili bildirimleri sil"""
    try:
        data = json.loads(request.body)
        notification_ids = data.get('notification_ids', [])
        
        if not notification_ids:
            return JsonResponse({
                'success': False,
                'message': 'Silinecek bildirim seçilmedi.'
            })
        
        deleted_count = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user
        ).delete()[0]
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} bildirim silindi.',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Delete selected notifications error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Bildirimler silinemedi.'
        })


@login_required
def notification_settings(request):
    """Bildirim ayarları sayfası"""
    user = request.user
    
    # Kullanıcı bildirim ayarlarını getir veya oluştur
    settings, created = UserNotificationSettings.objects.get_or_create(
        user=user,
        defaults={
            'email_notifications': True,
            'push_notifications': True,
            'job_applications': True,
            'job_matches': True,
            'new_messages': True,
            'post_interactions': True,
            'system_updates': True,
        }
    )
    
    if request.method == 'POST':
        try:
            # Ayarları güncelle
            settings.email_notifications = request.POST.get('email_notifications') == 'on'
            settings.sms_notifications = request.POST.get('sms_notifications') == 'on'
            settings.push_notifications = request.POST.get('push_notifications') == 'on'
            
            # İş bildirimleri
            settings.job_applications = request.POST.get('job_applications') == 'on'
            settings.job_matches = request.POST.get('job_matches') == 'on'
            settings.job_deadlines = request.POST.get('job_deadlines') == 'on'
            
            # Mesaj bildirimleri
            settings.new_messages = request.POST.get('new_messages') == 'on'
            settings.message_read_receipts = request.POST.get('message_read_receipts') == 'on'
            
            # Sosyal bildirimler
            settings.post_interactions = request.POST.get('post_interactions') == 'on'
            settings.new_followers = request.POST.get('new_followers') == 'on'
            
            # Sistem bildirimleri
            settings.system_updates = request.POST.get('system_updates') == 'on'
            settings.security_alerts = request.POST.get('security_alerts') == 'on'
            
            # Pazarlama bildirimleri
            settings.promotions = request.POST.get('promotions') == 'on'
            settings.newsletters = request.POST.get('newsletters') == 'on'
            
            # Sessiz saatler
            settings.quiet_hours_enabled = request.POST.get('quiet_hours_enabled') == 'on'
            if settings.quiet_hours_enabled:
                quiet_start = request.POST.get('quiet_hours_start')
                quiet_end = request.POST.get('quiet_hours_end')
                if quiet_start:
                    settings.quiet_hours_start = quiet_start
                if quiet_end:
                    settings.quiet_hours_end = quiet_end
            
            settings.save()
            
            messages.success(request, 'Bildirim ayarlarınız başarıyla güncellendi.')
            
        except Exception as e:
            logger.error(f"Notification settings update error: {str(e)}")
            messages.error(request, 'Ayarlar güncellenirken bir hata oluştu.')
        
        return redirect('notifications:settings')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'notifications/settings.html', context)


@login_required
def get_unread_count(request):
    """Okunmamış bildirim sayısını getir"""
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({
        'unread_count': unread_count
    })


@login_required
def get_recent_notifications(request):
    """Son bildirimleri getir (AJAX için)"""
    limit = int(request.GET.get('limit', 10))
    
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('notification_type').order_by('-created_at')[:limit]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': str(notification.id),
            'title': notification.title,
            'message': notification.short_message or notification.message[:100],
            'icon': notification.get_icon(),
            'color': notification.get_color(),
            'priority': notification.priority,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
            'action_text': notification.action_text,
        })
    
    return JsonResponse({
        'success': True,
        'notifications': notifications_data
    })


@login_required
def search_notifications(request):
    """Bildirim arama"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({
            'success': False,
            'notifications': []
        })
    
    notifications = Notification.objects.filter(
        recipient=request.user
    ).filter(
        Q(title__icontains=query) |
        Q(message__icontains=query)
    ).select_related('notification_type').order_by('-created_at')[:20]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': str(notification.id),
            'title': notification.title,
            'message': notification.message[:100] + '...' if len(notification.message) > 100 else notification.message,
            'type': notification.notification_type.name,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'url': f'/notifications/{notification.id}/',
        })
    
    return JsonResponse({
        'success': True,
        'notifications': notifications_data
    })


@login_required
@require_http_methods(["POST"])
def test_notification(request):
    """Test bildirimi gönder (development için)"""
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Bu özellik sadece yöneticiler için.'
        })
    
    try:
        notification = Notification.create_notification(
            recipient=request.user,
            notification_type_code='system_update',
            title='Test Bildirimi',
            message='Bu bir test bildirimidir. Sistem normal çalışıyor.',
            priority='normal',
            action_url='/notifications/',
            action_text='Bildirimleri Gör'
        )
        
        if notification:
            return JsonResponse({
                'success': True,
                'message': 'Test bildirimi gönderildi.',
                'notification_id': str(notification.id)
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Test bildirimi gönderilemedi.'
            })
            
    except Exception as e:
        logger.error(f"Test notification error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Test bildirimi gönderilirken hata oluştu.'
        })


# Webhook/API endpoints for external services
@csrf_exempt
@require_http_methods(["POST"])
def webhook_notification(request):
    """Harici servislerden bildirim alma (webhook)"""
    try:
        # API key kontrolü
        api_key = request.headers.get('X-API-Key')
        if api_key != getattr(settings, 'NOTIFICATION_WEBHOOK_API_KEY', None):
            return JsonResponse({
                'success': False,
                'message': 'Geçersiz API anahtarı.'
            }, status=401)
        
        data = json.loads(request.body)
        
        # Gerekli alanları kontrol et
        required_fields = ['recipient_id', 'notification_type', 'title', 'message']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'message': f'Eksik alan: {field}'
                }, status=400)
        
        # Kullanıcıyı bul
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            recipient = User.objects.get(id=data['recipient_id'])
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Kullanıcı bulunamadı.'
            }, status=404)
        
        # Bildirimi oluştur
        notification = Notification.create_notification(
            recipient=recipient,
            notification_type_code=data['notification_type'],
            title=data['title'],
            message=data['message'],
            priority=data.get('priority', 'normal'),
            action_url=data.get('action_url'),
            action_text=data.get('action_text'),
        )
        
        if notification:
            logger.info(f"Webhook notification created: {notification.id}")
            return JsonResponse({
                'success': True,
                'notification_id': str(notification.id)
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Bildirim oluşturulamadı.'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Geçersiz JSON formatı.'
        }, status=400)
    except Exception as e:
        logger.error(f"Webhook notification error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Sunucu hatası.'
        }, status=500)


@login_required
def notification_preferences_api(request):
    """Bildirim tercihlerini API olarak getir/güncelle"""
    settings, created = UserNotificationSettings.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'settings': {
                'email_notifications': settings.email_notifications,
                'sms_notifications': settings.sms_notifications,
                'push_notifications': settings.push_notifications,
                'job_applications': settings.job_applications,
                'job_matches': settings.job_matches,
                'job_deadlines': settings.job_deadlines,
                'new_messages': settings.new_messages,
                'message_read_receipts': settings.message_read_receipts,
                'post_interactions': settings.post_interactions,
                'new_followers': settings.new_followers,
                'system_updates': settings.system_updates,
                'security_alerts': settings.security_alerts,
                'promotions': settings.promotions,
                'newsletters': settings.newsletters,
                'quiet_hours_enabled': settings.quiet_hours_enabled,
                'quiet_hours_start': settings.quiet_hours_start.strftime('%H:%M') if settings.quiet_hours_start else '22:00',
                'quiet_hours_end': settings.quiet_hours_end.strftime('%H:%M') if settings.quiet_hours_end else '08:00',
            }
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Ayarları güncelle
            for key, value in data.items():
                if hasattr(settings, key):
                    if key in ['quiet_hours_start', 'quiet_hours_end']:
                        from datetime import datetime
                        setattr(settings, key, datetime.strptime(value, '%H:%M').time())
                    else:
                        setattr(settings, key, value)
            
            settings.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Ayarlar güncellendi.'
            })
            
        except Exception as e:
            logger.error(f"Update notification preferences error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Ayarlar güncellenemedi.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Desteklenmeyen HTTP metodu.'
    })
  
