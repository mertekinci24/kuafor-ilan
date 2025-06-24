from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PostLike, PostComment, PostSave

@receiver(post_save, sender=PostLike)
@receiver(post_delete, sender=PostLike)
def update_post_likes_count(sender, instance, **kwargs):
    """Post beğeni sayısını güncelle"""
    post = instance.post
    post.likes_count = post.likes.count()
    post.save(update_fields=['likes_count'])

@receiver(post_save, sender=PostComment)
@receiver(post_delete, sender=PostComment)
def update_post_comments_count(sender, instance, **kwargs):
    """Post yorum sayısını güncelle"""
    if not instance.is_deleted:
        post = instance.post
        post.comments_count = post.comments.filter(is_deleted=False).count()
        post.save(update_fields=['comments_count'])
        
