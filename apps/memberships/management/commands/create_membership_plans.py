from django.core.management.base import BaseCommand
from apps.memberships.models import SubscriptionPlan, PlanFeature

class Command(BaseCommand):
    help = 'Üyelik planlarını ve özelliklerini oluşturur'

    def handle(self, *args, **options):
        self.stdout.write('Üyelik planları oluşturuluyor...')

        # Mevcut planları sil (opsiyonel)
        if self.confirm_action('Mevcut planları silmek istiyor musunuz?'):
            SubscriptionPlan.objects.all().delete()
            self.stdout.write(self.style.WARNING('Mevcut planlar silindi.'))

        # 1. Ücretsiz Plan
        free_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='free',
            defaults={
                'name': 'Ücretsiz Plan',
                'price': 0,
                'billing_cycle': 'monthly',
                'max_job_posts': 1,
                'can_highlight_jobs': False,
                'can_feature_jobs': False,
                'cv_pool_access': False,
                'priority_support': False,
                'analytics_access': False,
                'is_active': True,
                'sort_order': 0
            }
        )
        self.stdout.write(f'✓ Ücretsiz Plan {"oluşturuldu" if created else "zaten mevcut"}')

        # 2. Temel Plan
        basic_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='basic',
            defaults={
                'name': 'Temel Plan',
                'price': 99,
                'billing_cycle': 'monthly',
                'max_job_posts': 5,
                'can_highlight_jobs': True,
                'can_feature_jobs': False,
                'cv_pool_access': False,
                'priority_support': False,
                'analytics_access': False,
                'is_active': True,
                'sort_order': 1
            }
        )
        self.stdout.write(f'✓ Temel Plan {"oluşturuldu" if created else "zaten mevcut"}')

        # 3. Profesyonel Plan
        pro_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='pro',
            defaults={
                'name': 'Profesyonel Plan',
                'price': 199,
                'billing_cycle': 'monthly',
                'max_job_posts': 999,  # Unlimited
                'can_highlight_jobs': True,
                'can_feature_jobs': True,
                'cv_pool_access': True,
                'priority_support': False,
                'analytics_access': True,
                'is_active': True,
                'sort_order': 2
            }
        )
        self.stdout.write(f'✓ Profesyonel Plan {"oluşturuldu" if created else "zaten mevcut"}')

        # 4. Kurumsal Plan
        enterprise_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='enterprise',
            defaults={
                'name': 'Kurumsal Plan',
                'price': 499,
                'billing_cycle': 'monthly',
                'max_job_posts': 999,  # Unlimited
                'can_highlight_jobs': True,
                'can_feature_jobs': True,
                'cv_pool_access': True,
                'priority_support': True,
                'analytics_access': True,
                'is_active': True,
                'sort_order': 3
            }
        )
        self.stdout.write(f'✓ Kurumsal Plan {"oluşturuldu" if created else "zaten mevcut"}')

        # Plan özelliklerini ekle
        self.create_plan_features(free_plan, basic_plan, pro_plan, enterprise_plan)

        self.stdout.write(self.style.SUCCESS('✅ Tüm üyelik planları başarıyla oluşturuldu!'))

    def create_plan_features(self, free_plan, basic_plan, pro_plan, enterprise_plan):
        """Plan özelliklerini oluştur"""
        
        features_data = [
            # Ücretsiz Plan Özellikleri
            (free_plan, 'Aylık 1 İlan', True, 1),
            (free_plan, 'Temel Profil', True, 2),
            (free_plan, 'Email Desteği', True, 3),
            
            # Temel Plan Özellikleri
            (basic_plan, 'Aylık 5 İlan', True, 1),
            (basic_plan, 'İlan Öne Çıkarma', True, 2),
            (basic_plan, 'Gelişmiş Profil', True, 3),
            (basic_plan, 'Email Desteği', True, 4),
            
            # Profesyonel Plan Özellikleri
            (pro_plan, 'Sınırsız İlan', True, 1),
            (pro_plan, 'İlan Öne Çıkarma', True, 2),
            (pro_plan, 'Öne Çıkan İlan', True, 3),
            (pro_plan, 'CV Havuzu Erişimi', True, 4),
            (pro_plan, 'Analitik Raporları', True, 5),
            (pro_plan, 'Email Desteği', True, 6),
            
            # Kurumsal Plan Özellikleri
            (enterprise_plan, 'Sınırsız İlan', True, 1),
            (enterprise_plan, 'İlan Öne Çıkarma', True, 2),
            (enterprise_plan, 'Öne Çıkan İlan', True, 3),
            (enterprise_plan, 'CV Havuzu Erişimi', True, 4),
            (enterprise_plan, 'Gelişmiş Analitik', True, 5),
            (enterprise_plan, 'Öncelikli Destek', True, 6),
            (enterprise_plan, 'API Erişimi', True, 7),
        ]

        for plan, feature_name, is_included, sort_order in features_data:
            PlanFeature.objects.get_or_create(
                plan=plan,
                feature_name=feature_name,
                defaults={
                    'is_included': is_included,
                    'sort_order': sort_order
                }
            )

        self.stdout.write('✓ Plan özellikleri oluşturuldu')

    def confirm_action(self, message):
        """Kullanıcıdan onay al"""
        response = input(f'{message} (y/N): ')
        return response.lower() in ['y', 'yes', 'evet', 'e']