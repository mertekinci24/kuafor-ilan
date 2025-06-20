from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    """Abstract base model with soft delete functionality"""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()
      
