from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from apps.core.models import TimeStampedModel, SoftDeleteModel
from decimal import Decimal

# CUSTOM MANAGERS - Modellerin üstünde tanımlanmalı
class CategoryManager(models.Manager):
    """Soft delete edilen kategorileri otomatik filtreleyen manager"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class BrandManager(models.Manager):
    """Soft delete edilen markaları otomatik filtreleyen manager"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class ProductManager(models.Manager):
    """Soft delete edilen ürünleri otomatik filtreleyen manager"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def with_deleted(self):
        """Silinen ürünleri de dahil et"""
        return super().get_queryset()
    
    def deleted_only(self):
        """Sadece silinen ürünler"""
        return super().get_queryset().filter(is_deleted=True)


class ProductCategory(TimeStampedModel, SoftDeleteModel):
    """Ürün kategorileri (Saç Bakım, Makyaj, Nail Art, vs.)"""
    
    name = models.CharField(max_length=100, verbose_name='Kategori Adı')
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Açıklama')
    
    # Görsel
    image = models.ImageField(
        upload_to='categories/', 
        blank=True, 
        verbose_name='Kategori Görseli'
    )
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    
    # Custom Manager
    objects = CategoryManager()  # Sadece aktif (silinmeyen) kategoriler
    all_objects = models.Manager()  # Tüm kategoriler
    sort_order = models.PositiveIntegerField(default=0, verbose_name='Sıralama')
    
    # İstatistik
    product_count = models.PositiveIntegerField(default=0, verbose_name='Ürün Sayısı')
    
    # Custom Manager
    objects = CategoryManager()  # Sadece aktif (silinmeyen) kategoriler
    all_objects = models.Manager()  # Tüm kategoriler
    
    class Meta:
        verbose_name = 'Ürün Kategorisi'
        verbose_name_plural = 'Ürün Kategorileri'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category', kwargs={'slug': self.slug})
    
    def update_product_count(self):
        """Kategori ürün sayısını güncelle"""
        self.product_count = self.products.filter(is_active=True).count()
        self.save(update_fields=['product_count'])


class BrandManager(models.Manager):
    """Soft delete edilen markaları otomatik filtreleyen manager"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class ProductBrand(TimeStampedModel, SoftDeleteModel):
    """Ürün markaları (L'Oreal, Schwarzkopf, vs.)"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name='Marka Adı')
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Marka Açıklaması')
    
    # Görsel
    logo = models.ImageField(
        upload_to='brands/', 
        blank=True, 
        verbose_name='Marka Logosu'
    )
    
    # İletişim
    website = models.URLField(blank=True, verbose_name='Website')
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    
    class Meta:
        verbose_name = 'Marka'
        verbose_name_plural = 'Markalar'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductManager(models.Manager):
    """Soft delete edilen ürünleri otomatik filtreleyen manager"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def with_deleted(self):
        """Silinen ürünleri de dahil et"""
        return super().get_queryset()
    
    def deleted_only(self):
        """Sadece silinen ürünler"""
        return super().get_queryset().filter(is_deleted=True)


class Product(TimeStampedModel, SoftDeleteModel):
    """Ana ürün modeli"""
    
    STATUS_CHOICES = (
        ('active', 'Aktif'),
        ('inactive', 'Pasif'),
        ('out_of_stock', 'Stokta Yok'),
        ('discontinued', 'Üretimi Durduruldu'),
    )
    
    # Temel Bilgiler
    name = models.CharField(max_length=200, verbose_name='Ürün Adı')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(verbose_name='Ürün Açıklaması')
    short_description = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Kısa Açıklama'
    )
    
    # Kategori ve Marka
    category = models.ForeignKey(
        ProductCategory, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name='Kategori'
    )
    brand = models.ForeignKey(
        ProductBrand, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name='Marka'
    )
    
    # Fiyat Bilgileri
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Fiyat'
    )
    compare_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Karşılaştırma Fiyatı (İndirim öncesi)'
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Maliyet Fiyatı'
    )
    
    # Stok
    sku = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='SKU (Stok Kodu)'
    )
    stock_quantity = models.PositiveIntegerField(
        default=0, 
        verbose_name='Stok Miktarı'
    )
    low_stock_threshold = models.PositiveIntegerField(
        default=10, 
        verbose_name='Düşük Stok Uyarı Seviyesi'
    )
    
    # Fiziksel Özellikler
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Ağırlık (gr)'
    )
    dimensions = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='Boyutlar (cm)'
    )
    
    # Görseller
    main_image = models.ImageField(
        upload_to='products/', 
        verbose_name='Ana Ürün Görseli'
    )
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    keywords = models.CharField(
        max_length=200, 
        blank=True, 
        help_text='Virgül ile ayırın'
    )
    
    # Durum
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name='Durum'
    )
    is_featured = models.BooleanField(
        default=False, 
        verbose_name='Öne Çıkan Ürün'
    )
    
    # İstatistikler
    view_count = models.PositiveIntegerField(default=0)
    order_count = models.PositiveIntegerField(default=0)
    
    # Premium Kullanıcı İndirimi
    premium_discount_percent = models.PositiveIntegerField(
        default=0, 
        verbose_name='Premium Üye İndirimi (%)'
    )
    
    # Custom Managers
    objects = ProductManager()  # Sadece aktif (silinmeyen) ürünler
    all_objects = models.Manager()  # Tüm ürünler (silinenleri de dahil)
    
    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['brand', 'status']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.brand.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.brand.name}")
        
        # Short description otomatik oluştur
        if not self.short_description and self.description:
            self.short_description = self.description[:200]
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def discount_amount(self):
        """İndirim miktarı"""
        if self.compare_price and self.compare_price > self.price:
            return self.compare_price - self.price
        return Decimal('0.00')
    
    @property
    def discount_percentage(self):
        """İndirim yüzdesi"""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    def get_premium_price(self):
        """Premium kullanıcı fiyatı"""
        if self.premium_discount_percent > 0:
            discount = (self.price * self.premium_discount_percent) / 100
            return self.price - discount
        return self.price
    
    def get_profit_margin(self):
        """Kar marjı"""
        if self.cost_price:
            return self.price - self.cost_price
        return Decimal('0.00')
    
    def soft_delete_product(self):
        """Ürünü soft delete yap ve status'ü de güncelle"""
        self.soft_delete()  # SoftDeleteModel'den gelen metod
        self.status = 'discontinued'
        self.save()
    
    def restore_product(self):
        """Ürünü geri getir"""
        self.restore()  # SoftDeleteModel'den gelen metod
        self.status = 'active'
        self.save()
    
    @property
    def is_available_for_sale(self):
        """Satışa uygun mu? (silinmemiş + aktif + stokta)"""
        return (
            not self.is_deleted and 
            self.status == 'active' and 
            self.is_in_stock
        )


class ProductImage(TimeStampedModel):
    """Ürün ek görselleri"""
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Ürün Görseli'
        verbose_name_plural = 'Ürün Görselleri'
        ordering = ['sort_order']
    
    def __str__(self):
        return f"{self.product.name} - Görsel {self.sort_order}"


class ProductReview(TimeStampedModel):
    """Ürün yorumları"""
    
    RATING_CHOICES = (
        (1, '1 Yıldız'),
        (2, '2 Yıldız'),
        (3, '3 Yıldız'),
        (4, '4 Yıldız'),
        (5, '5 Yıldız'),
    )
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200, verbose_name='Başlık')
    comment = models.TextField(verbose_name='Yorum')
    
    # Durum
    is_approved = models.BooleanField(default=False, verbose_name='Onaylandı')
    
    class Meta:
        verbose_name = 'Ürün Yorumu'
        verbose_name_plural = 'Ürün Yorumları'
        unique_together = ('product', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.rating} yıldız"
        