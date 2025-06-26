# Mesajlaşma signal'ları buraya eklenecek
# Şimdilik boş bırakıyoruz

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Message, Conversation


@receiver(post_save, sender=Message)
def update_conversation_on_message(sender, instance, created, **kwargs):
    """Yeni mesaj geldiğinde sohbeti güncelle"""
    if created:
        # Sohbetin son mesaj bilgilerini güncelle
        conversation = instance.conversation
        conversation.last_message = instance.content[:100]
        conversation.last_message_at = instance.created_at
        conversation.last_message_sender = instance.sender
        conversation.save(update_fields=['last_message', 'last_message_at', 'last_message_sender', 'updated_at'])


# Gelecekte eklenebilecek signal'lar:
# - Mesaj okundu bildirimi
# - Email/SMS gönderimi
# - Real-time bildirimler
