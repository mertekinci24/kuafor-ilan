from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max
from django.utils import timezone
import json
import logging

from .models import Conversation, Message, BlockedUser, MessageReport
from apps.jobs.models import JobListing

User = get_user_model()
logger = logging.getLogger(__name__)


@login_required
def messages_list(request):
    """Mesajlar ana sayfası - sohbet listesi"""
    user = request.user
    
    # Kullanıcının katıldığı sohbetler
    conversations = Conversation.objects.filter(
        participants=user,
        is_active=True
    ).select_related('last_message_sender').prefetch_related('participants').order_by('-updated_at')
    
    # Sohbet bilgilerini hazırla
    conversations_data = []
    for conv in conversations:
        other_participant = conv.get_other_participant(user)
        if other_participant:
            unread_count = conv.get_unread_count(user)
            conversations_data.append({
                'conversation': conv,
                'other_participant': other_participant,
                'unread_count': unread_count,
                'last_message_preview': conv.last_message[:50] + '...' if conv.last_message and len(conv.last_message) > 50 else conv.last_message,
            })
    
    # Toplam okunmamış mesaj sayısı
    total_unread = sum(conv_data['unread_count'] for conv_data in conversations_data)
    
    context = {
        'conversations_data': conversations_data,
        'total_unread': total_unread,
        'user': user,
    }
    
    return render(request, 'messages/list.html', context)


@login_required
def conversation_detail(request, conversation_id):
    """Sohbet detayı"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    other_participant = conversation.get_other_participant(request.user)
    
    # Mesajları getir
    messages_qs = conversation.messages.filter(
        is_deleted=False
    ).select_related('sender', 'shared_job').order_by('created_at')
    
    # Sayfalama
    paginator = Paginator(messages_qs, 50)
    page_number = request.GET.get('page', 1)
    messages_page = paginator.get_page(page_number)
    
    # Okunmamış mesajları okundu olarak işaretle
    unread_messages = conversation.messages.filter(
        sender=other_participant,
        is_read=False
    )
    unread_messages.update(is_read=True, read_at=timezone.now())
    
    # Engelleme durumunu kontrol et
    is_blocked = BlockedUser.objects.filter(
        Q(blocker=request.user, blocked=other_participant) |
        Q(blocker=other_participant, blocked=request.user)
    ).exists()
    
    context = {
        'conversation': conversation,
        'other_participant': other_participant,
        'messages': messages_page.object_list,
        'messages_page': messages_page,
        'is_blocked': is_blocked,
        'user': request.user,
    }
    
    return render(request, 'messages/detail.html', context)


@login_required
def start_conversation(request, user_id):
    """Yeni sohbet başlat veya mevcut sohbete git"""
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        messages.error(request, 'Kendinizle mesajlaşamazsınız.')
        return redirect('messages:list')
    
    # Engelleme kontrolü
    if BlockedUser.objects.filter(
        Q(blocker=request.user, blocked=other_user) |
        Q(blocker=other_user, blocked=request.user)
    ).exists():
        messages.error(request, 'Bu kullanıcıyla mesajlaşamazsınız.')
        return redirect('messages:list')
    
    # Mevcut sohbet var mı kontrol et
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if not conversation:
        # Yeni sohbet oluştur
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
        
        # Hoş geldin mesajı gönder
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=f"Merhaba! Size mesaj göndermek istedim.",
            message_type='text'
        )
        
        logger.info(f"New conversation started between {request.user.email} and {other_user.email}")
    
    return redirect('messages:detail', conversation_id=conversation.id)


@login_required
@require_http_methods(["POST"])
def send_message(request, conversation_id):
    """Mesaj gönder"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    other_participant = conversation.get_other_participant(request.user)
    
    # Engelleme kontrolü
    if BlockedUser.objects.filter(
        Q(blocker=request.user, blocked=other_participant) |
        Q(blocker=other_participant, blocked=request.user)
    ).exists():
        return JsonResponse({
            'success': False,
            'message': 'Bu kullanıcıyla mesajlaşamazsınız.'
        })
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'text')
        shared_job_id = data.get('shared_job_id')
        
        if not content and message_type == 'text':
            return JsonResponse({
                'success': False,
                'message': 'Mesaj içeriği boş olamaz.'
            })
        
        # Mesaj oluştur
        message_data = {
            'conversation': conversation,
            'sender': request.user,
            'content': content,
            'message_type': message_type,
        }
        
        # İş ilanı paylaşımı
        if message_type == 'job_share' and shared_job_id:
            try:
                job = JobListing.objects.get(id=shared_job_id, status='active')
                message_data['shared_job'] = job
                message_data['content'] = f"İş ilanı paylaştı: {job.title}"
            except JobListing.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Paylaşılacak iş ilanı bulunamadı.'
                })
        
        message = Message.objects.create(**message_data)
        
        # Sohbeti güncelle
        conversation.update_last_message(message)
        
        logger.info(f"Message sent from {request.user.email} to {other_participant.email}")
        
        return JsonResponse({
            'success': True,
            'message_id': str(message.id),
            'message': 'Mesaj gönderildi.',
            'created_at': message.created_at.isoformat(),
        })
        
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Mesaj gönderilemedi.'
        })


@login_required
@require_http_methods(["POST"])
def upload_message_file(request, conversation_id):
    """Mesaja dosya yükle"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    if 'file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'message': 'Dosya seçilmedi.'
        })
    
    file = request.FILES['file']
    
    # Dosya boyutu kontrolü (10MB)
    if file.size > 10 * 1024 * 1024:
        return JsonResponse({
            'success': False,
            'message': 'Dosya boyutu 10MB\'dan büyük olamaz.'
        })
    
    try:
        # Dosya türüne göre mesaj oluştur
        if file.content_type.startswith('image/'):
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=f"Resim gönderdi: {file.name}",
                message_type='image',
                image=file
            )
        else:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=f"Dosya gönderdi: {file.name}",
                message_type='file',
                file=file
            )
        
        return JsonResponse({
            'success': True,
            'message_id': str(message.id),
            'message': 'Dosya başarıyla gönderildi.',
        })
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Dosya yüklenemedi.'
        })


@login_required
@require_http_methods(["POST"])
def block_user(request, user_id):
    """Kullanıcıyı engelle"""
    user_to_block = get_object_or_404(User, id=user_id)
    
    if user_to_block == request.user:
        return JsonResponse({
            'success': False,
            'message': 'Kendinizi engelleyemezsiniz.'
        })
    
    blocked_user, created = BlockedUser.objects.get_or_create(
        blocker=request.user,
        blocked=user_to_block,
        defaults={'reason': 'Kullanıcı engellendi'}
    )
    
    if created:
        # Mevcut sohbetleri deaktive et
        conversations = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=user_to_block
        )
        conversations.update(is_active=False)
        
        return JsonResponse({
            'success': True,
            'message': 'Kullanıcı engellendi.'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Kullanıcı zaten engellenmiş.'
        })


@login_required
@require_http_methods(["POST"])
def unblock_user(request, user_id):
    """Kullanıcının engelini kaldır"""
    user_to_unblock = get_object_or_404(User, id=user_id)
    
    try:
        blocked_user = BlockedUser.objects.get(
            blocker=request.user,
            blocked=user_to_unblock
        )
        blocked_user.delete()
        
        # Sohbetleri tekrar aktive et
        conversations = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=user_to_unblock
        )
        conversations.update(is_active=True)
        
        return JsonResponse({
            'success': True,
            'message': 'Kullanıcının engeli kaldırıldı.'
        })
        
    except BlockedUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Kullanıcı zaten engellenmiş değil.'
        })


@login_required
@require_http_methods(["POST"])
def report_message(request, message_id):
    """Mesajı şikayet et"""
    message = get_object_or_404(Message, id=message_id)
    
    # Kendi mesajını şikayet edemez
    if message.sender == request.user:
        return JsonResponse({
            'success': False,
            'message': 'Kendi mesajınızı şikayet edemezsiniz.'
        })
    
    try:
        data = json.loads(request.body)
        reason = data.get('reason', 'other')
        description = data.get('description', '')
        
        report, created = MessageReport.objects.get_or_create(
            message=message,
            reporter=request.user,
            defaults={
                'reason': reason,
                'description': description
            }
        )
        
        if created:
            logger.info(f"Message reported: {message.id} by {request.user.email}")
            return JsonResponse({
                'success': True,
                'message': 'Şikayetiniz alındı. İnceleme süreci başlatıldı.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Bu mesajı daha önce şikayet etmişsiniz.'
            })
            
    except Exception as e:
        logger.error(f"Report message error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Şikayet gönderilemedi.'
        })


@login_required
@require_http_methods(["POST"])
def delete_message(request, message_id):
    """Mesajı sil"""
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    
    if message.is_deleted:
        return JsonResponse({
            'success': False,
            'message': 'Mesaj zaten silinmiş.'
        })
    
    message.is_deleted = True
    message.deleted_at = timezone.now()
    message.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Mesaj silindi.'
    })


@login_required
def search_conversations(request):
    """Sohbet arama"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({
            'success': False,
            'conversations': []
        })
    
    # Katıldığı sohbetlerde arama yap
    conversations = Conversation.objects.filter(
        participants=request.user,
        is_active=True
    ).filter(
        Q(participants__first_name__icontains=query) |
        Q(participants__last_name__icontains=query) |
        Q(participants__email__icontains=query) |
        Q(last_message__icontains=query)
    ).distinct().select_related('last_message_sender').prefetch_related('participants')[:10]
    
    results = []
    for conv in conversations:
        other_participant = conv.get_other_participant(request.user)
        if other_participant:
            results.append({
                'id': str(conv.id),
                'other_participant': {
                    'id': other_participant.id,
                    'name': other_participant.get_full_name() or other_participant.email,
                    'avatar': other_participant.first_name[0].upper() if other_participant.first_name else 'U'
                },
                'last_message': conv.last_message,
                'updated_at': conv.updated_at.isoformat(),
            })
    
    return JsonResponse({
        'success': True,
        'conversations': results
    })


@login_required
def blocked_users_list(request):
    """Engellenen kullanıcılar listesi"""
    blocked_users = BlockedUser.objects.filter(
        blocker=request.user
    ).select_related('blocked').order_by('-blocked_at')
    
    context = {
        'blocked_users': blocked_users,
    }
    
    return render(request, 'messages/blocked_users.html', context)


# API Views for real-time features
@login_required
def get_unread_count(request):
    """Okunmamış mesaj sayısını getir"""
    unread_count = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    
    return JsonResponse({
        'unread_count': unread_count
    })


@login_required
def mark_conversation_read(request, conversation_id):
    """Sohbeti okundu olarak işaretle"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    # Karşı taraftan gelen okunmamış mesajları işaretle
    unread_messages = conversation.messages.exclude(
        sender=request.user
    ).filter(is_read=False)
    
    updated_count = unread_messages.update(
        is_read=True, 
        read_at=timezone.now()
    )
    
    return JsonResponse({
        'success': True,
        'marked_count': updated_count
    })


@login_required
def get_conversation_messages(request, conversation_id):
    """Sohbet mesajlarını JSON olarak getir (AJAX için)"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    page = int(request.GET.get('page', 1))
    messages_qs = conversation.messages.filter(
        is_deleted=False
    ).select_related('sender', 'shared_job').order_by('-created_at')
    
    paginator = Paginator(messages_qs, 20)
    messages_page = paginator.get_page(page)
    
    messages_data = []
    for message in messages_page:
        message_data = {
            'id': str(message.id),
            'content': message.content,
            'sender': {
                'id': message.sender.id,
                'name': message.sender.get_full_name() or message.sender.email,
                'is_me': message.sender == request.user
            },
            'message_type': message.message_type,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read,
        }
        
        if message.image:
            message_data['image_url'] = message.image.url
        
        if message.file:
            message_data['file_url'] = message.file.url
            message_data['file_name'] = message.get_file_name()
        
        if message.shared_job:
            message_data['shared_job'] = {
                'id': message.shared_job.id,
                'title': message.shared_job.title,
                'company': message.shared_job.business.get_full_name(),
                'url': f'/jobs/{message.shared_job.id}/'
            }
        
        messages_data.append(message_data)
    
    return JsonResponse({
        'success': True,
        'messages': messages_data,
        'has_next': messages_page.has_next(),
        'has_previous': messages_page.has_previous(),
        'current_page': messages_page.number,
        'total_pages': messages_page.paginator.num_pages,
    })
  
