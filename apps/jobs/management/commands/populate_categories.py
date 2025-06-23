from django.core.management.base import BaseCommand
from apps.jobs.models import JobCategory


class Command(BaseCommand):
    help = 'Temel iş kategorilerini veritabanına ekler'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Temel kategoriler ekleniyor...')
        
        categories = [
            {'name': 'Kadın Kuaförü', 'description': 'Kadın kuaförlüğü hizmetleri'},
            {'name': 'Erkek Kuaförü', 'description': 'Erkek kuaförlüğü ve berberlik hizmetleri'},
            {'name': 'Makyaj Uzmanı', 'description': 'Makyaj ve güzellik uzmanı'},
            {'name': 'Nail Art Uzmanı', 'description': 'Nail art ve manikür uzmanı'},
            {'name': 'Saç Uzmanı', 'description': 'Saç bakımı ve styling uzmanı'},
            {'name': 'Güzellik Uzmanı', 'description': 'Genel güzellik hizmetleri'},
            {'name': 'Masöz', 'description': 'Masaj ve terapi uzmanı'},
            {'name': 'Kaş-Kirpik Uzmanı', 'description': 'Kaş şekillendirme ve kirpik uzmanı'},
        ]

        created_count = 0
        existing_count = 0

        for cat_data in categories:
            category, created = JobCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {category.name} kategorisi oluşturuldu')
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f'ℹ️ {category.name} kategorisi zaten mevcut')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 İşlem tamamlandı!\n'
                f'📊 Oluşturulan: {created_count}\n'
                f'📋 Mevcut olan: {existing_count}\n'
                f'📈 Toplam kategori: {JobCategory.objects.count()}'
            )
        )
      
