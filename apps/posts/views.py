# apps/posts/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.utils import timezone
from django.contrib import messages
import json
import logging

from .models import (
    Post, PostCategory, PostLike, PostComment, PostCommentLike,
    PostSave, PostShare, PostView, Poll, PollOption, PollVote,
    Event, EventParticipant
)

User = get_user_model()
logger = logging.getLogger(__name__)


def posts_list_view(request):
    """Post listesi - Ana sayfa feed'i"""
    # Get filter parameters
    category_slug = request.GET.get('category')
    post_type = request.GET.get('type')
    search = request.GET.get('search')
    
    # Base queryset
    posts = Post.objects.filter(
        is_published=True,
        is_approved=True,
        is_deleted=False
    ).select_related(
        'author', 'category'
    ).prefetch_related(
        'likes', 'comments', 'poll', 'event'
    )
    
    # Apply filters
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    if post_type:
        posts = posts.filter(post_type=post_type)
    
    if search:
        posts = posts.filter(
            Q(content__icontains=search) |
            Q(title__icontains=search) |
            Q(tags__icontains=search) |
            Q(author__first_name__icontains=search) |
            Q(author__last_name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = PostCategory.objects.filter(is_active=True)
    
    # Process posts for template
    processed_posts = []
    for post in posts_page:
        post_data = {
            'post': post,
            'is_liked': post.is_liked_by(request.user) if request.user.is_authenticated else False,
            'is_saved': post.is_saved_by(request.user) if request.user.is_authenticated else False,
            'tags_list': post.get_tags_list(),
            'can_edit': request.user == post.author if request.user.is_authenticated else False,
        }
        
        # Add poll data if exists
        if hasattr(post, 'poll'):
            poll = post.poll
            post_data['poll'] = {
                'question': poll.question,
                'options': poll.options.all(),
                'total_votes': poll.total_votes,
                'can_vote': poll.can_vote(request.user) if request.user.is_authenticated else False,
                'is_expired': poll.is_expired(),
            }
        
        # Add event data if exists
        if hasattr(post, 'event'):
            event = post.event
            post_data['event'] = {
                'title': event.title,
                'start_date': event.start_date,
                'location_name': event.location_name,
                'is_online': event.is_online,
                'participants_count': event.participants_count,
                'is_past': event.is_past(),
                'is_full': event.is_full(),
            }
        
        processed_posts.append(post_data)
    
    context = {
        'posts': processed_posts,
        'posts_page': posts_page,
        'categories': categories,
        'current_category': category_slug,
        'current_type': post_type,
        'search_query': search,
    }
    
    return render(request, 'posts/list.html', context)


@login_required
def post_create_view(request):
    """Post oluşturma"""
    if request.method == 'POST':
        try:
            # Basic post data
            content = request.POST.get('content', '').strip()
            title = request.POST.get('title', '').strip()
            post_type = request.POST.get('post_type', 'text')
            category_id = request.POST.get('category')
            tags = request.POST.get('tags', '')
            location = request.POST.get('location', '')
            visibility = request.POST.get('visibility', 'public')
            
            if not content:
                messages.error(request, 'İçerik boş olamaz.')
                return redirect('home')
            
            # Create post
            post = Post.objects.create(
                author=request.user,
                content=content,
                title=title,
                post_type=post_type,
                tags=tags,
                location=location,
                visibility=visibility,
                category_id=category_id if category_id else None
            )
            
            # Handle media uploads
            if 'image' in request.FILES:
                post.image = request.FILES['image']
                post.save()
            
            if 'video' in request.FILES:
                post.video = request.FILES['video']
                post.save()
            
            # Handle link sharing
            if post_type == 'link':
                post.link_url = request.POST.get('link_url', '')
                post.link_title = request.POST.get('link_title', '')
                post.link_description = request.POST.get('link_description', '')
                post.save()
            
            # Handle poll creation
            if post_type == 'poll':
                poll_question = request.POST.get('poll_question', '')
                poll_options = request.POST.getlist('poll_options[]')
                multiple_choice = request.POST.get('multiple_choice') == 'on'
                
                if poll_question and len(poll_options) >= 2:
                    poll = Poll.objects.create(
                        post=post,
                        question=poll_question,
                        multiple_choice=multiple_choice
                    )
                    
                    for option_text in poll_options:
                        if option_text.strip():
                            PollOption.objects.create(
                                poll=poll,
                                text=option_text.strip()
                            )
            
            # Handle event creation
            if post_type == 'event':
                event_title = request.POST.get('event_title', '')
                event_description = request.POST.get('event_description', '')
                start_date = request.POST.get('start_date')
                location_name = request.POST.get('location_name', '')
                is_online = request.POST.get('is_online') == 'on'
                
                if event_title and start_date:
                    Event.objects.create(
                        post=post,
                        title=event_title,
                        description=event_description,
                        start_date=start_date,
                        location_name=location_name,
                        is_online=is_online
                    )
            
            messages.success(request, 'Gönderiniz başarıyla paylaşıldı!')
            logger.info(f"New post created by {request.user.email}: {post.id}")
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Gönderi başarıyla oluşturuldu',
                    'post_id': str(post.id)
                })
            
            return redirect('home')
            
        except Exception as e:
            logger.error(f"Post creation error: {str(e)}")
            messages.error(request, 'Gönderi oluşturulurken hata oluştu.')
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': 'Gönderi oluşturulamadı'
                })
            
            return redirect('home')
    
    # GET request - show form
    categories = PostCategory.objects.filter(is_active=True)
    return render(request, 'posts/create.html', {'categories': categories})


def post_detail_view(request, pk):
    """Post detay sayfası"""
    post = get_object_or_404(
        Post.objects.select_related('author', 'category'),
        pk=pk,
        is_published=True,
        is_approved=True,
        is_deleted=False
    )
    
    # Track view
    if request.user != post.author:
        PostView.objects.get_or_create(
            post=post,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            defaults={
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
        )
    
    # Get comments
    comments = post.comments.filter(
        is_deleted=False,
        parent=None
    ).select_related('author').prefetch_related('replies')
    
    context = {
        'post': post,
        'comments': comments,
        'is_liked': post.is_liked_by(request.user) if request.user.is_authenticated else False,
        'is_saved': post.is_saved_by(request.user) if request.user.is_authenticated else False,
        'tags_list': post.get_tags_list(),
        'can_edit': request.user == post.author if request.user.is_authenticated else False,
    }
    
    return render(request, 'posts/detail.html', context)


@login_required
def post_edit_view(request, pk):
    """Post düzenleme"""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        post.content = request.POST.get('content', post.content)
        post.title = request.POST.get('title', post.title)
        post.tags = request.POST.get('tags', post.tags)
        post.location = request.POST.get('location', post.location)
        post.visibility = request.POST.get('visibility', post.visibility)
        
        category_id = request.POST.get('category')
        post.category_id = category_id if category_id else None
        
        post.save()
        messages.success(request, 'Gönderiniz başarıyla güncellendi!')
        return redirect('posts:detail', pk=post.pk)
    
    categories = PostCategory.objects.filter(is_active=True)
    return render(request, 'posts/edit.html', {
        'post': post,
        'categories': categories,
        'tags_list': post.get_tags_list()
    })


@login_required
def post_delete_view(request, pk):
    """Post silme"""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        post.is_deleted = True
        post.save()
        messages.success(request, 'Gönderiniz silindi.')
        return redirect('home')
    
    return render(request, 'posts/delete.html', {'post': post})


# API Views
@login_required
@require_http_methods(["POST"])
def post_like_api(request):
    """Post beğenme/beğenmeme API"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        
        post = get_object_or_404(Post, pk=post_id)
        like, created = PostLike.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if not created:
            like.delete()
            is_liked = False
            action = 'unliked'
        else:
            is_liked = True
            action = 'liked'
        
        return JsonResponse({
            'success': True,
            'action': action,
            'is_liked': is_liked,
            'likes_count': post.likes_count
        })
        
    except Exception as e:
        logger.error(f"Post like error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Beğeni işlemi başarısız'
        })


@login_required
@require_http_methods(["POST"])
def post_save_api(request):
    """Post kaydetme/kaydetmeme API"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        
        post = get_object_or_404(Post, pk=post_id)
        save, created = PostSave.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if not created:
            save.delete()
            is_saved = False
            action = 'unsaved'
        else:
            is_saved = True
            action = 'saved'
        
        return JsonResponse({
            'success': True,
            'action': action,
            'is_saved': is_saved
        })
        
    except Exception as e:
        logger.error(f"Post save error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Kaydetme işlemi başarısız'
        })


@login_required
@require_http_methods(["POST"])
def post_share_api(request):
    """Post paylaşma API"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        shared_to = data.get('shared_to', 'timeline')
        note = data.get('note', '')
        
        post = get_object_or_404(Post, pk=post_id)
        
        PostShare.objects.create(
            post=post,
            user=request.user,
            shared_to=shared_to,
            note=note
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Gönderi başarıyla paylaşıldı',
            'shares_count': post.shares_count
        })
        
    except Exception as e:
        logger.error(f"Post share error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Paylaşım başarısız'
        })


@require_http_methods(["POST"])
def post_view_api(request):
    """Post görüntülenme API"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        
        post = get_object_or_404(Post, pk=post_id)
        
        # Don't track author's own views
        if request.user.is_authenticated and request.user == post.author:
            return JsonResponse({'success': True})
        
        PostView.objects.get_or_create(
            post=post,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            defaults={
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
        )
        
        return JsonResponse({
            'success': True,
            'views_count': post.views_count
        })
        
    except Exception as e:
        logger.error(f"Post view error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Görüntülenme kaydedilemedi'
        })


def comments_api(request):
    """Yorumları getir API"""
    post_id = request.GET.get('post_id')
    if not post_id:
        return JsonResponse({'success': False, 'message': 'Post ID gerekli'})
    
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.filter(is_deleted=False, parent=None).select_related('author')
    
    comments_data = []
    for comment in comments:
        comment_data = {
            'id': comment.id,
            'content': comment.content,
            'author': {
                'name': comment.author.get_full_name(),
                'avatar': comment.author.first_name[0].upper() if comment.author.first_name else 'U'
            },
            'created_at': comment.created_at.isoformat(),
            'likes_count': comment.likes_count,
            'replies': []
        }
        
        # Add replies
        for reply in comment.get_replies():
            reply_data = {
                'id': reply.id,
                'content': reply.content,
                'author': {
                    'name': reply.author.get_full_name(),
                    'avatar': reply.author.first_name[0].upper() if reply.author.first_name else 'U'
                },
                'created_at': reply.created_at.isoformat(),
                'likes_count': reply.likes_count,
            }
            comment_data['replies'].append(reply_data)
        
        comments_data.append(comment_data)
    
    return JsonResponse({
        'success': True,
        'comments': comments_data
    })


@login_required
@require_http_methods(["POST"])
def comment_create_api(request):
    """Yorum oluşturma API"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')
        
        if not content:
            return JsonResponse({
                'success': False,
                'message': 'Yorum içeriği boş olamaz'
            })
        
        post = get_object_or_404(Post, pk=post_id)
        
        if not post.allow_comments:
            return JsonResponse({
                'success': False,
                'message': 'Bu gönderiye yorum yapılamaz'
            })
        
        parent = None
        if parent_id:
            parent = get_object_or_404(PostComment, pk=parent_id, post=post)
        
        comment = PostComment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent=parent
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Yorum başarıyla eklendi',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author': {
                    'name': comment.author.get_full_name(),
                    'avatar': comment.author.first_name[0].upper() if comment.author.first_name else 'U'
                },
                'created_at': comment.created_at.isoformat(),
                'likes_count': 0
            }
        })
        
    except Exception as e:
        logger.error(f"Comment create error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Yorum eklenemedi'
        })


@login_required
@require_http_methods(["POST"])
def poll_vote_api(request):
    """Anket oylama API"""
    try:
        data = json.loads(request.body)
        poll_id = data.get('poll_id')
        option_ids = data.get('option_ids', [])
        
        poll = get_object_or_404(Poll, pk=poll_id)
        
        if not poll.can_vote(request.user):
            return JsonResponse({
                'success': False,
                'message': 'Bu ankete oy veremezsiniz'
            })
        
        if not option_ids:
            return JsonResponse({
                'success': False,
                'message': 'En az bir seçenek seçmelisiniz'
            })
        
        # Check multiple choice
        if not poll.multiple_choice and len(option_ids) > 1:
            return JsonResponse({
                'success': False,
                'message': 'Bu ankette sadece bir seçenek seçebilirsiniz'
            })
        
        # Create votes
        for option_id in option_ids:
            option = get_object_or_404(PollOption, pk=option_id, poll=poll)
            PollVote.objects.create(
                poll=poll,
                option=option,
                user=request.user
            )
        
        # Get updated results
        poll.refresh_from_db()
        options_data = []
        for option in poll.options.all():
            options_data.append({
                'id': option.id,
                'text': option.text,
                'votes_count': option.votes_count,
                'percentage': option.get_percentage()
            })
        
        return JsonResponse({
            'success': True,
            'message': 'Oyunuz kaydedildi',
            'poll': {
                'total_votes': poll.total_votes,
                'options': options_data
            }
        })
        
    except Exception as e:
        logger.error(f"Poll vote error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Oy kaydedilemedi'
        })


def feed_api(request):
    """Feed API - Infinite scroll için"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 5))
    
    posts = Post.objects.filter(
        is_published=True,
        is_approved=True,
        is_deleted=False
    ).select_related('author', 'category')[(page-1)*page_size:page*page_size]
    
    posts_data = []
    for post in posts:
        post_data = {
            'id': str(post.id),
            'content': post.content,
            'author': {
                'name': post.author.get_full_name(),
                'avatar': post.author.first_name[0].upper() if post.author.first_name else 'U'
            },
            'created_at': post.created_at.isoformat(),
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'is_liked': post.is_liked_by(request.user) if request.user.is_authenticated else False,
        }
        posts_data.append(post_data)
    
    return JsonResponse({
        'success': True,
        'posts': posts_data,
        'has_more': len(posts) == page_size
    })


def trending_api(request):
    """Trend konular API"""
    # This would be implemented with proper trending algorithm
    # For now, return mock data
    trending_data = [
        {'tag': 'kuaförilanları', 'count': 1234},
        {'tag': 'berbertrendleri', 'count': 892},
        {'tag': 'saçmodelleri', 'count': 756},
        {'tag': 'güzelliksalonu', 'count': 634},
        {'tag': 'profesyonelgelişim', 'count': 523},
    ]
    
    return JsonResponse({
        'success': True,
        'trending': trending_data
    })
  
