from django.core.management.base import BaseCommand
from apps.products.models import ProductCategory, ProductBrand, Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Güzellik sektörü için kategoriler, markalar ve örnek ürünler oluşturur (kuaför, güzellik merkezi, kozmetik, makyaj, tırnak)'

    def handle(self, *args, **options):
        self.stdout.write('Güzellik sektörü e-commerce ürünleri oluşturuluyor...')

        # Mevcut ürünleri sil (opsiyonel)
        if self.confirm_action('Mevcut ürünleri silmek istiyor musunuz?'):
            Product.objects.all().delete()
            ProductBrand.objects.all().delete()
            ProductCategory.objects.all().delete()
            self.stdout.write(self.style.WARNING('Mevcut ürünler silindi.'))

        # 1. KATEGORİLER OLUŞTUR - GÜZELLİK SEKTÖRÜ GENEL
        categories_data = [
            {
                'name': 'Saç Bakım Ürünleri',
                'description': 'Şampuan, saç kremi, maske, serum ve saç bakım ürünleri',
                'sort_order': 1
            },
            {
                'name': 'Saç Boyaları ve Kimyasalları',
                'description': 'Profesyonel saç boyaları, perma, keratin, açıcılar',
                'sort_order': 2
            },
            {
                'name': 'Kuaför Aletleri',
                'description': 'Makas, fön, düzleştirici, maşa, clipper, tıraş makinesi',
                'sort_order': 3
            },
            {
                'name': 'Makyaj Ürünleri',
                'description': 'Fondöten, ruj, rimel, far, allık, kapatıcı, primer',
                'sort_order': 4
            },
            {
                'name': 'Makyaj Fırçaları ve Aletleri',
                'description': 'Makyaj fırçaları, sünger, aplikatör, makyaj çantası',
                'sort_order': 5
            },
            {
                'name': 'Tırnak Ürünleri',
                'description': 'Oje, nail art, tırnak bakım, kalıcı oje, akrilik',
                'sort_order': 6
            },
            {
                'name': 'Tırnak Aletleri',
                'description': 'Tırnak makası, eğe, törpü, cuticle aleti, UV lamba',
                'sort_order': 7
            },
            {
                'name': 'Cilt Bakım Ürünleri',
                'description': 'Temizleyici, tonik, serum, nemlendirici, maske',
                'sort_order': 8
            },
            {
                'name': 'Güneş Koruyucu Ürünler',
                'description': 'SPF kremler, güneş koruyucu spreyleri, after sun',
                'sort_order': 9
            },
            {
                'name': 'Parfüm ve Kozmetik',
                'description': 'Parfüm, deodorant, vücut spreyi, kozmetik ürünler',
                'sort_order': 10
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = ProductCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            self.stdout.write(f'✓ {cat_data["name"]} {"oluşturuldu" if created else "zaten mevcut"}')

        # 2. MARKALAR OLUŞTUR
        brands_data = [
            {'name': 'L\'Oréal Professional', 'description': 'Dünya lideri saç bakım markası'},
            {'name': 'Schwarzkopf', 'description': 'Alman profesyonel saç bakım markası'},
            {'name': 'Wella Professionals', 'description': 'Profesyonel kuaför ürünleri'},
            {'name': 'MAC Cosmetics', 'description': 'Profesyonel makyaj markası'},
            {'name': 'Urban Decay', 'description': 'Premium kozmetik markası'},
            {'name': 'OPI', 'description': 'Profesyonel nail art ürünleri'},
            {'name': 'Babyliss', 'description': 'Saç şekillendirme aletleri'},
            {'name': 'La Roche Posay', 'description': 'Dermatolojik cilt bakım'},
            {'name': 'Real Techniques', 'description': 'Makyaj fırçaları'},
            {'name': 'Gelish', 'description': 'Kalıcı oje sistemi'}
        ]

        brands = {}
        for brand_data in brands_data:
            brand, created = ProductBrand.objects.get_or_create(
                name=brand_data['name'],
                defaults=brand_data
            )
            brands[brand_data['name']] = brand
            self.stdout.write(f'✓ {brand_data["name"]} {"oluşturuldu" if created else "zaten mevcut"}')

        # 3. ÖRNEK ÜRÜNLER OLUŞTUR
        products_data = [
            {
                'name': 'Serie Expert Absolut Repair Şampuan 300ml',
                'category': 'Saç Bakım Ürünleri',
                'brand': 'L\'Oréal Professional',
                'price': Decimal('89.90'),
                'compare_price': Decimal('109.90'),
                'sku': 'LOR-SHA-001',
                'stock_quantity': 50,
                'description': 'Hasarlı saçlar için onarıcı şampuan. Protein içeriği ile saçları güçlendirir.',
                'premium_discount_percent': 15
            },
            {
                'name': 'Koleston Perfect Saç Boyası 7/0',
                'category': 'Saç Boyaları ve Kimyasalları',
                'brand': 'Wella Professionals',
                'price': Decimal('45.50'),
                'compare_price': Decimal('55.00'),
                'sku': 'WEL-BOY-701',
                'stock_quantity': 80,
                'description': 'Profesyonel kalıcı saç boyası. %100 beyaz saç kapatma garantisi.',
                'premium_discount_percent': 20
            },
            {
                'name': 'Professional Kuaför Makası 6 inch',
                'category': 'Kuaför Aletleri',
                'brand': 'Babyliss',
                'price': Decimal('450.00'),
                'compare_price': Decimal('520.00'),
                'sku': 'BAB-MAK-601',
                'stock_quantity': 25,
                'description': 'Paslanmaz çelik profesyonel kuaför makası. Ergonomik tasarım.',
                'premium_discount_percent': 25
            },
            {
                'name': 'Studio Fix Fluid Foundation',
                'category': 'Makyaj Ürünleri',
                'brand': 'MAC Cosmetics',
                'price': Decimal('195.00'),
                'sku': 'MAC-FON-001',
                'stock_quantity': 40,
                'description': 'Orta-yoğun kapatıcılık sağlayan fondöten. 24 saat kalıcı.',
                'premium_discount_percent': 10
            },
            {
                'name': 'Everyday Eye Brush Set',
                'category': 'Makyaj Fırçaları ve Aletleri',
                'brand': 'Real Techniques',
                'price': Decimal('85.00'),
                'compare_price': Decimal('110.00'),
                'sku': 'REA-BRU-001',
                'stock_quantity': 20,
                'description': '5 parçalık göz makyajı fırça seti. Sentetik kıllar.',
                'premium_discount_percent': 20
            },
            {
                'name': 'Nail Lacquer - Big Apple Red',
                'category': 'Tırnak Ürünleri',
                'brand': 'OPI',
                'price': Decimal('65.00'),
                'sku': 'OPI-OJE-001',
                'stock_quantity': 60,
                'description': 'Klasik kırmızı oje. Uzun süre kalıcı formül.',
                'premium_discount_percent': 15
            },
            {
                'name': 'Toleriane Caring Wash',
                'category': 'Cilt Bakım Ürünleri',
                'brand': 'La Roche Posay',
                'price': Decimal('85.00'),
                'sku': 'LRP-WAS-001',
                'stock_quantity': 40,
                'description': 'Hassas ciltler için temizleyici. Paraben içermez.',
                'premium_discount_percent': 12
            }
        ]

        # Ürünleri oluştur
        for product_data in products_data:
            # Kategori ve brand objelerini bul
            category = categories[product_data['category']]
            brand = brands[product_data['brand']]
            
            # Ürün verisinden kategori ve brand string'lerini çıkar
            product_data_clean = product_data.copy()
            del product_data_clean['category']
            del product_data_clean['brand']
            
            # Ürünü oluştur
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults={
                    **product_data_clean,
                    'category': category,
                    'brand': brand,
                    'status': 'active',
                    'is_featured': False
                }
            )
            
            if created:
                self.stdout.write(f'✓ {product.name} oluşturuldu')
            else:
                self.stdout.write(f'- {product.name} zaten mevcut')

        # Kategori ürün sayılarını güncelle
        for category in categories.values():
            category.update_product_count()

        self.stdout.write(self.style.SUCCESS('✅ Güzellik sektörü e-commerce sistemi başarıyla kuruldu!'))
        self.stdout.write(self.style.SUCCESS(f'📊 {len(categories)} kategori, {len(brands)} marka, {len(products_data)} ürün oluşturuldu'))

    def confirm_action(self, message):
        """Kullanıcıdan onay al"""
        response = input(f'{message} (y/N): ')
        return response.lower() in ['y', 'yes', 'evet', 'e']
        