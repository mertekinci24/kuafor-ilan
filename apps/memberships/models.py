from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import TimeStampedModel
from decimal import Decimal

class SubscriptionPlan(TimeStampedModel):
    """Üyelik planları (Free, Basic, Pro, Enterprise)"""
    
    PLAN_TYPE_CHOICES = (
        ('free', 'Ücretsiz'),
        ('basic', 'Temel'),
        ('pro', 'Profesyonel'),
        ('enterprise', 'Kurumsal'),
    )
    
    BILLING_CYCLE_CHOICES = (
        ('monthly', 'Aylık'),
        ('quarterly', '3 Aylık'),
        ('yearly', 'Yıllık'),
    )
    
    name = models.CharField(max_length=50, verbose_name='Plan Adı')
    plan_type = models.CharField(
        max_length=20, 
        choices=PLAN_TYPE_CHOICES, 
        unique=True,
        verbose_name='Plan Tipi'
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Fiyat'
    )
    billing_cycle = models.CharField(
        max_length=20, 
        choices=BILLING_CYCLE_CHOICES,
        default='monthly',
        verbose_name='Faturalama Döngüsü'
    )
    
    # Plan Özellikleri
    max_job_posts = models.PositiveIntegerField(
        default=1, 
        verbose_name='Maksimum İlan Sayısı'
    )
    can_highlight_jobs = models.BooleanField(
        default=False, 
        verbose_name='İlan Öne Çıkarma'
    )
    can_feature_jobs = models.BooleanField(
        default=False, 
        verbose_name='Öne Çıkan İlan'
    )
    cv_pool_access = models.BooleanField(
        default=False, 
        verbose_name='CV Havuzu Erişimi'
    )
    priority_support = models.BooleanField(
        default=False, 
        verbose_name='Öncelikli Destek'
    )
    analytics_access = models.BooleanField(
        default=False, 
        verbose_name='Analitik Erişimi'
    )
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='Sıralama')
    
    class Meta:
        verbose_name = 'Üyelik Planı'
        verbose_name_plural = 'Üyelik Planları'
        ordering = ['sort_order', 'price']
    
    def __str__(self):
        return f"{self.name} - ₺{self.price}/{self.get_billing_cycle_display()}"
    
    def get_monthly_price(self):
        """Aylık fiyata çevir"""
        if self.billing_cycle == 'monthly':
            return self.price
        elif self.billing_cycle == 'quarterly':
            return self.price / 3
        elif self.billing_cycle == 'yearly':
            return self.price / 12
        return self.price


class UserMembership(TimeStampedModel):
    """Kullanıcıların aktif üyelikleri"""
    
    STATUS_CHOICES = (
        ('active', 'Aktif'),
        ('cancelled', 'İptal Edildi'),
        ('expired', 'Süresi Doldu'),
        ('suspended', 'Askıya Alındı'),
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='membership'
    )
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.PROTECT,
        verbose_name='Plan'
    )
    
    # Tarihler
    start_date = models.DateTimeField(verbose_name='Başlangıç Tarihi')
    end_date = models.DateTimeField(verbose_name='Bitiş Tarihi')
    
    # Durum
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name='Durum'
    )
    
    # Otomatik yenileme
    auto_renew = models.BooleanField(default=True, verbose_name='Otomatik Yenileme')
    
    # Kullanım istatistikleri (mevcut dönem için)
    jobs_posted_this_period = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Kullanıcı Üyeliği'
        verbose_name_plural = 'Kullanıcı Üyelikleri'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.plan.name}"
    
    def is_active(self):
        """Üyelik aktif mi?"""
        return (
            self.status == 'active' and 
            self.end_date > timezone.now()
        )
    
    def days_remaining(self):
        """Kalan gün sayısı"""
        if self.end_date > timezone.now():
            return (self.end_date - timezone.now()).days
        return 0
    
    def can_post_job(self):
        """Yeni iş ilanı verebilir mi?"""
        if not self.is_active():
            return False
        return self.jobs_posted_this_period < self.plan.max_job_posts
    
    def remaining_job_posts(self):
        """Kalan ilan hakkı"""
        if not self.is_active():
            return 0
        return max(0, self.plan.max_job_posts - self.jobs_posted_this_period)


class MembershipPayment(TimeStampedModel):
    """Üyelik ödemeleri"""
    
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
        ('refunded', 'İade Edildi'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Kredi Kartı'),
        ('bank_transfer', 'Banka Havalesi'),
        ('iyzico', 'İyzico'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='membership_payments'
    )
    membership = models.ForeignKey(
        UserMembership, 
        on_delete=models.CASCADE,
        related_name='payments'
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    
    # Ödeme Bilgileri
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        default='iyzico'
    )
    
    # Durum
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Ödeme sistemi bilgileri
    payment_provider_id = models.CharField(max_length=200, blank=True)
    payment_provider_response = models.JSONField(default=dict, blank=True)
    
    # Fatura bilgileri
    invoice_number = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Üyelik Ödemesi'
        verbose_name_plural = 'Üyelik Ödemeleri'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - ₺{self.amount} - {self.get_status_display()}"


class PlanFeature(TimeStampedModel):
    """Plan özelliklerinin detaylı açıklamaları"""
    
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.CASCADE,
        related_name='features'
    )
    feature_name = models.CharField(max_length=100, verbose_name='Özellik Adı')
    feature_description = models.TextField(blank=True, verbose_name='Açıklama')
    is_included = models.BooleanField(default=True, verbose_name='Dahil mi?')
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Plan Özelliği'
        verbose_name_plural = 'Plan Özellikleri'
        ordering = ['plan', 'sort_order']
    
    def __str__(self):
        return f"{self.plan.name} - {self.feature_name}"


class MembershipUpgrade(TimeStampedModel):
    """Üyelik yükseltme istekleri"""
    
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='upgrade_requests'
    )
    current_plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.PROTECT,
        related_name='current_upgrades'
    )
    requested_plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.PROTECT,
        related_name='requested_upgrades'
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Fiyat farkı
    price_difference = models.DecimalField(max_digits=10, decimal_places=2)
    
    # İşlem tarihleri
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Üyelik Yükseltme'
        verbose_name_plural = 'Üyelik Yükseltmeleri'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()}: {self.current_plan.name} → {self.requested_plan.name}"