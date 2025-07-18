# Generated by Django 4.2.8 on 2025-07-01 10:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, verbose_name='Ürün Adı')),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True)),
                ('description', models.TextField(verbose_name='Ürün Açıklaması')),
                ('short_description', models.CharField(blank=True, max_length=200, verbose_name='Kısa Açıklama')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Fiyat')),
                ('compare_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Karşılaştırma Fiyatı (İndirim öncesi)')),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Maliyet Fiyatı')),
                ('sku', models.CharField(max_length=50, unique=True, verbose_name='SKU (Stok Kodu)')),
                ('stock_quantity', models.PositiveIntegerField(default=0, verbose_name='Stok Miktarı')),
                ('low_stock_threshold', models.PositiveIntegerField(default=10, verbose_name='Düşük Stok Uyarı Seviyesi')),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Ağırlık (gr)')),
                ('dimensions', models.CharField(blank=True, max_length=100, verbose_name='Boyutlar (cm)')),
                ('main_image', models.ImageField(upload_to='products/', verbose_name='Ana Ürün Görseli')),
                ('meta_title', models.CharField(blank=True, max_length=60)),
                ('meta_description', models.CharField(blank=True, max_length=160)),
                ('keywords', models.CharField(blank=True, help_text='Virgül ile ayırın', max_length=200)),
                ('status', models.CharField(choices=[('active', 'Aktif'), ('inactive', 'Pasif'), ('out_of_stock', 'Stokta Yok'), ('discontinued', 'Üretimi Durduruldu')], default='active', max_length=20, verbose_name='Durum')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Öne Çıkan Ürün')),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('order_count', models.PositiveIntegerField(default=0)),
                ('premium_discount_percent', models.PositiveIntegerField(default=0, verbose_name='Premium Üye İndirimi (%)')),
            ],
            options={
                'verbose_name': 'Ürün',
                'verbose_name_plural': 'Ürünler',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductBrand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Marka Adı')),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True)),
                ('description', models.TextField(blank=True, verbose_name='Marka Açıklaması')),
                ('logo', models.ImageField(blank=True, upload_to='brands/', verbose_name='Marka Logosu')),
                ('website', models.URLField(blank=True, verbose_name='Website')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
            ],
            options={
                'verbose_name': 'Marka',
                'verbose_name_plural': 'Markalar',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Kategori Adı')),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True)),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
                ('image', models.ImageField(blank=True, upload_to='categories/', verbose_name='Kategori Görseli')),
                ('meta_title', models.CharField(blank=True, max_length=60)),
                ('meta_description', models.CharField(blank=True, max_length=160)),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Sıralama')),
                ('product_count', models.PositiveIntegerField(default=0, verbose_name='Ürün Sayısı')),
            ],
            options={
                'verbose_name': 'Ürün Kategorisi',
                'verbose_name_plural': 'Ürün Kategorileri',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to='products/gallery/')),
                ('alt_text', models.CharField(blank=True, max_length=200)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product')),
            ],
            options={
                'verbose_name': 'Ürün Görseli',
                'verbose_name_plural': 'Ürün Görselleri',
                'ordering': ['sort_order'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.productbrand', verbose_name='Marka'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.productcategory', verbose_name='Kategori'),
        ),
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rating', models.PositiveIntegerField(choices=[(1, '1 Yıldız'), (2, '2 Yıldız'), (3, '3 Yıldız'), (4, '4 Yıldız'), (5, '5 Yıldız')])),
                ('title', models.CharField(max_length=200, verbose_name='Başlık')),
                ('comment', models.TextField(verbose_name='Yorum')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Onaylandı')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='products.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ürün Yorumu',
                'verbose_name_plural': 'Ürün Yorumları',
                'ordering': ['-created_at'],
                'unique_together': {('product', 'user')},
            },
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['status', 'is_featured'], name='products_pr_status_28f1d7_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'status'], name='products_pr_categor_75eeb5_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['brand', 'status'], name='products_pr_brand_i_6bc83e_idx'),
        ),
    ]
