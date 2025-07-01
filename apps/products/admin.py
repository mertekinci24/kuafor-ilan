from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    ProductCategory, 
    ProductBrand, 
    Product, 
    ProductImage, 
    ProductReview
)

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'product_count', 'is_active', 'is_deleted', 
        'sort_order', 'created_at'
    ]
    list_filter = ['is_active', 'is_deleted', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Ayarlar', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Soft Delete Bilgisi', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['product_count', 'deleted_at']
    
    # Bulk actions
    actions = ['soft_delete_categories', 'restore_categories']
    
    def soft_delete_categories(self, request, queryset):
        for category in queryset:
            category.soft_delete()
        self.message_user(request, f"{queryset.count()} kategori soft delete edildi.")
    soft_delete_categories.short_description = "Seçilen kategorileri soft delete yap"
    
    def restore_categories(self, request, queryset):
        for category in queryset:
            category.restore()
        self.message_user(request, f"{queryset.count()} kategori geri getirildi.")
    restore_categories.short_description = "Seçilen kategorileri geri getir"
    
    def get_queryset(self, request):
        """Admin panelinde silinenleri de göster"""
        return ProductCategory.all_objects.all()
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Ürün sayısını güncelle
        obj.update_product_count()


@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['is_active', 'is_deleted', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'logo')
        }),
        ('İletişim', {
            'fields': ('website',)
        }),
        ('Ayarlar', {
            'fields': ('is_active',)
        }),
        ('Soft Delete Bilgisi', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['deleted_at']
    
    # Bulk actions
    actions = ['soft_delete_brands', 'restore_brands']
    
    def soft_delete_brands(self, request, queryset):
        for brand in queryset:
            brand.soft_delete()
        self.message_user(request, f"{queryset.count()} marka soft delete edildi.")
    soft_delete_brands.short_description = "Seçilen markaları soft delete yap"
    
    def restore_brands(self, request, queryset):
        for brand in queryset:
            brand.restore()
        self.message_user(request, f"{queryset.count()} marka geri getirildi.")
    restore_brands.short_description = "Seçilen markaları geri getir"
    
    def get_queryset(self, request):
        """Admin panelinde silinenleri de göster"""
        return ProductBrand.all_objects.all()


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ['image', 'alt_text', 'sort_order']
    ordering = ['sort_order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'brand', 'category', 'price_display', 
        'stock_status', 'status', 'is_featured', 'is_deleted', 'view_count'
    ]
    list_filter = [
        'status', 'is_featured', 'is_deleted', 'category', 'brand', 
        'created_at'
    ]
    search_fields = [
        'name', 'description', 'sku', 
        'brand__name', 'category__name'
    ]
    prepopulated_fields = {'slug': ('name', 'brand')}
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': (
                'name', 'slug', 'description', 'short_description',
                'category', 'brand', 'main_image'
            )
        }),
        ('Fiyat ve Stok', {
            'fields': (
                'price', 'compare_price', 'cost_price',
                'sku', 'stock_quantity', 'low_stock_threshold'
            )
        }),
        ('Fiziksel Özellikler', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'keywords'),
            'classes': ('collapse',)
        }),
        ('Ayarlar', {
            'fields': (
                'status', 'is_featured', 'premium_discount_percent'
            )
        }),
        ('İstatistikler', {
            'fields': ('view_count', 'order_count'),
            'classes': ('collapse',)
        }),
        ('Soft Delete Bilgisi', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['view_count', 'order_count', 'deleted_at']
    inlines = [ProductImageInline]
    
    # Listede özel görünümler
    def price_display(self, obj):
        price_html = f"₺{obj.price}"
        if obj.compare_price and obj.compare_price > obj.price:
            price_html += f" <small style='text-decoration: line-through; color: #666;'>₺{obj.compare_price}</small>"
            price_html += f" <span style='color: #28a745;'>%{obj.discount_percentage} İNDİRİM</span>"
        return format_html(price_html)
    price_display.short_description = 'Fiyat'
    
    def stock_status(self, obj):
        if obj.is_deleted:
            return format_html('<span style="color: gray;">Soft Delete</span>')
        elif obj.stock_quantity <= 0:
            return format_html('<span style="color: red;">Stokta Yok</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: orange;">Düşük Stok ({})</span>', obj.stock_quantity)
        else:
            return format_html('<span style="color: green;">Stokta ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'Stok Durumu'
    
    # Bulk actions - Soft Delete sistemli
    actions = [
        'make_featured', 'remove_featured', 'mark_as_active', 'mark_as_inactive',
        'soft_delete_products', 'restore_products'
    ]
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} ürün öne çıkan olarak işaretlendi.")
    make_featured.short_description = "Seçilen ürünleri öne çıkan yap"
    
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} ürün öne çıkan olmaktan çıkarıldı.")
    remove_featured.short_description = "Seçilen ürünleri öne çıkan olmaktan çıkar"
    
    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} ürün aktif olarak işaretlendi.")
    mark_as_active.short_description = "Seçilen ürünleri aktif yap"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(status='inactive')
        self.message_user(request, f"{queryset.count()} ürün pasif olarak işaretlendi.")
    mark_as_inactive.short_description = "Seçilen ürünleri pasif yap"
    
    def soft_delete_products(self, request, queryset):
        for product in queryset:
            product.soft_delete_product()
        self.message_user(request, f"{queryset.count()} ürün soft delete edildi.")
    soft_delete_products.short_description = "Seçilen ürünleri soft delete yap"
    
    def restore_products(self, request, queryset):
        for product in queryset:
            product.restore_product()
        self.message_user(request, f"{queryset.count()} ürün geri getirildi.")
    restore_products.short_description = "Seçilen ürünleri geri getir"
    
    def get_queryset(self, request):
        """Admin panelinde silinenleri de göster"""
        return Product.all_objects.select_related('category', 'brand')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'alt_text', 'sort_order']
    list_filter = ['created_at']
    search_fields = ['product__name', 'alt_text']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "Görsel Yok"
    image_preview.short_description = 'Önizleme'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'user', 'rating_display', 
        'title', 'is_approved', 'created_at'
    ]
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__email', 'title', 'comment']
    
    fieldsets = (
        ('Yorum Bilgileri', {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        ('Moderasyon', {
            'fields': ('is_approved',)
        }),
    )
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating
        return format_html(f'{stars} ({obj.rating}/5)')
    rating_display.short_description = 'Değerlendirme'
    
    # Bulk actions
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} yorum onaylandı.")
    approve_reviews.short_description = "Seçilen yorumları onayla"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} yorumun onayı kaldırıldı.")
    disapprove_reviews.short_description = "Seçilen yorumların onayını kaldır"

# Admin site başlık güncellemeleri
admin.site.site_header = "Kuaförİlan E-Commerce Yönetimi"
admin.site.site_title = "Kuaförİlan Admin"
admin.site.index_title = "E-Commerce Yönetim Paneli"
