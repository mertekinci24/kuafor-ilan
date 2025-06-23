# setup.sh - Quick setup script
#!/bin/bash

echo "🚀 Kuaför İlan Platformu Kurulum Başlıyor..."

# Virtual environment oluştur
echo "📦 Virtual environment oluşturuluyor..."
python -m venv venv

# Virtual environment'ı aktifleştir
echo "🔧 Virtual environment aktifleştiriliyor..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Requirements yükle
echo "📚 Bağımlılıklar yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt

# Environment dosyası oluştur
echo "⚙️ Environment dosyası oluşturuluyor..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env dosyası oluşturuldu. Lütfen gerekli ayarları yapın."
fi

# Database migration
echo "🗄️ Database migration çalıştırılıyor..."
python manage.py makemigrations
python manage.py migrate

# Admin kullanıcı oluştur
echo "👤 Admin kullanıcı oluşturuluyor..."
python manage.py create_admin

# Kategorileri yükle
echo "📂 Temel kategoriler yükleniyor..."
python manage.py populate_categories

# Static files toplama
echo "📁 Static dosyalar toplanıyor..."
python manage.py collectstatic --noinput

echo "🎉 Kurulum tamamlandı!"
echo ""
echo "📍 Başlatmak için: python manage.py runserver"
echo "🔐 Admin Panel: http://127.0.0.1:8000/admin/"
echo "👤 Admin Giriş: admin@kuaforilan.com / admin123"
echo ""

---

# dev_commands.sh - Development helper commands
#!/bin/bash

case "$1" in
    "setup")
        echo "🚀 Development setup başlatılıyor..."
        bash setup.sh
        ;;
    "reset-db")
        echo "🗄️ Database sıfırlanıyor..."
        rm -f db.sqlite3
        python manage.py makemigrations
        python manage.py migrate
        python manage.py create_admin
        python manage.py populate_categories
        echo "✅ Database sıfırlandı!"
        ;;
    "migrate")
        echo "🔄 Migration çalıştırılıyor..."
        python manage.py makemigrations
        python manage.py migrate
        ;;
    "admin")
        echo "👤 Admin kullanıcı oluşturuluyor..."
        python manage.py create_admin
        ;;
    "categories")
        echo "📂 Kategoriler yükleniyor..."
        python manage.py populate_categories
        ;;
    "collect")
        echo "📁 Static dosyalar toplanıyor..."
        python manage.py collectstatic --noinput
        ;;
    "test")
        echo "🧪 Testler çalıştırılıyor..."
        python manage.py test
        ;;
    "shell")
        echo "🐚 Django shell açılıyor..."
        python manage.py shell
        ;;
    "run")
        echo "🏃 Sunucu başlatılıyor..."
        python manage.py runserver
        ;;
    "deploy")
        echo "🚀 Production deployment hazırlığı..."
        python manage.py collectstatic --noinput
        python manage.py migrate
        python manage.py create_admin
        echo "✅ Deployment hazır!"
        ;;
    *)
        echo "📋 Available commands:"
        echo "  setup      - Full development setup"
        echo "  reset-db   - Reset database"
        echo "  migrate    - Run migrations"
        echo "  admin      - Create admin user"
        echo "  categories - Load job categories"
        echo "  collect    - Collect static files"
        echo "  test       - Run tests"
        echo "  shell      - Open Django shell"
        echo "  run        - Start development server"
        echo "  deploy     - Prepare for deployment"
        echo ""
        echo "Usage: bash dev_commands.sh <command>"
        ;;
esac

---

# create_sample_data.py - Management command to create sample data
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.jobs.models import JobCategory, JobListing
from apps.authentication.models import JobSeekerProfile, BusinessProfile
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create',
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=20,
            help='Number of job listings to create',
        )

    def handle(self, *args, **options):
        self.stdout.write('🎭 Sample data oluşturuluyor...')
        
        # Sample cities
        cities = ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana']
        
        # Create job seekers
        self.stdout.write('👥 İş arayan kullanıcılar oluşturuluyor...')
        for i in range(options['users'] // 2):
            user = User.objects.create_user(
                username=f'jobseeker{i}@example.com',
                email=f'jobseeker{i}@example.com',
                password='testpass123',
                first_name=f'İş{i}',
                last_name=f'Arayan{i}',
                user_type='jobseeker'
            )
            
            JobSeekerProfile.objects.create(
                user=user,
                city=random.choice(cities),
                experience_years=random.choice([0, 1, 2, 3, 5, 10]),
                skills='Saç kesimi, Boyama, Perma, Makyaj',
                bio=f'Deneyimli kuaför. {random.randint(1, 10)} yıl tecrübe.',
                is_available=True
            )

        # Create businesses
        self.stdout.write('🏢 İş veren kullanıcılar oluşturuluyor...')
        for i in range(options['users'] // 2):
            user = User.objects.create_user(
                username=f'business{i}@example.com',
                email=f'business{i}@example.com',
                password='testpass123',
                first_name=f'Salon{i}',
                last_name=f'Sahibi{i}',
                user_type='business'
            )
            
            BusinessProfile.objects.create(
                user=user,
                company_name=f'Güzellik Salonu {i}',
                city=random.choice(cities),
                address=f'Test Mahallesi {i}. Sokak No: {i}',
                contact_phone=f'+90555000{i:04d}',
                company_description=f'Modern ve kaliteli hizmet veren güzellik salonu {i}.'
            )

        # Create job listings
        self.stdout.write('💼 İş ilanları oluşturuluyor...')
        categories = JobCategory.objects.all()
        businesses = User.objects.filter(user_type='business')
        
        job_titles = [
            'Deneyimli Kuaför Aranıyor',
            'Berber Arıyoruz',
            'Saç Uzmanı İş İlanı',
            'Güzellik Uzmanı Aranıyor',
            'Makyaj Uzmanı İş İlanı',
            'Nail Art Uzmanı Aranıyor'
        ]
        
        for i in range(options['jobs']):
            business = random.choice(businesses)
            category = random.choice(categories)
            
            JobListing.objects.create(
                business=business,
                title=random.choice(job_titles),
                description=f'Kaliteli ve deneyimli {category.name.lower()} arıyoruz. '
                           f'Esnek çalışma saatleri, rekabetçi maaş imkanları. '
                           f'Detaylı bilgi için başvurun.',
                category=category,
                city=random.choice(cities),
                salary_min=random.randint(5000, 8000),
                salary_max=random.randint(8000, 15000),
                is_urgent=random.choice([True, False]),
                status='active',
                views_count=random.randint(10, 100)
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Sample data oluşturuldu!\n'
                f'👥 {options["users"]} kullanıcı\n'
                f'💼 {options["jobs"]} iş ilanı\n'
                f'🔑 Test giriş: jobseeker0@example.com / testpass123'
            )
        )

---

# test_basic.py - Basic tests
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.jobs.models import JobCategory, JobListing

User = get_user_model()

class BasicFunctionalityTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test users
        self.job_seeker = User.objects.create_user(
            username='jobseeker@test.com',
            email='jobseeker@test.com',
            password='testpass123',
            user_type='jobseeker'
        )
        
        self.business = User.objects.create_user(
            username='business@test.com',
            email='business@test.com',
            password='testpass123',
            user_type='business'
        )
        
        # Create test category
        self.category = JobCategory.objects.create(
            name='Test Kuaför',
            description='Test kategorisi'
        )
        
        # Create test job
        self.job = JobListing.objects.create(
            business=self.business,
            title='Test İş İlanı',
            description='Test açıklaması',
            category=self.category,
            city='İstanbul',
            salary_min=5000,
            salary_max=8000
        )

    def test_home_page(self):
        """Ana sayfa testi"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kuaför İlan')

    def test_jobs_list(self):
        """İş ilanları listesi testi"""
        response = self.client.get(reverse('jobs:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.job.title)

    def test_job_detail(self):
        """İş ilanı detay testi"""
        response = self.client.get(reverse('jobs:detail', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.job.title)
        self.assertContains(response, self.job.description)

    def test_login_page(self):
        """Login sayfası testi"""
        response = self.client.get(reverse('authentication:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Giriş Yap')

    def test_register_page(self):
        """Register sayfası testi"""
        response = self.client.get(reverse('authentication:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hesap Oluştur')

    def test_user_login(self):
        """Kullanıcı giriş testi"""
        response = self.client.post(reverse('authentication:login'), {
            'username': 'jobseeker@test.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_job_application(self):
        """İş başvurusu testi"""
        # Login first
        self.client.login(username='jobseeker@test.com', password='testpass123')
        
        response = self.client.post(
            reverse('jobs:apply', kwargs={'job_id': self.job.id}),
            {'cover_letter': 'Test başvuru yazısı'},
            content_type='application/x-www-form-urlencoded'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_user(self):
        """Kullanıcı kayıt testi"""
        response = self.client.post(reverse('authentication:register'), {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'newuser@test.com',
            'password': 'testpass123',
            'user_type': 'jobseeker'
        })
        
        # Check if user was created
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())

    def test_invalid_login(self):
        """Geçersiz giriş testi"""
        response = self.client.post(reverse('authentication:login'), {
            'username': 'invalid@test.com',
            'password': 'wrongpass'
        })
        
        self.assertEqual(response.status_code, 200)  # Stays on login page
        self.assertContains(response, 'hatalı')  # Contains error message

---

# load_test_data.py - Quick test data loader
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuafor_ilan.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.jobs.models import JobCategory, JobListing
from apps.authentication.models import JobSeekerProfile, BusinessProfile

User = get_user_model()

def create_test_data():
    print("🎭 Test veriler oluşturuluyor...")
    
    # Create test job seeker
    if not User.objects.filter(email='test@jobseeker.com').exists():
        user = User.objects.create_user(
            username='test@jobseeker.com',
            email='test@jobseeker.com',
            password='test123',
            first_name='Test',
            last_name='JobSeeker',
            user_type='jobseeker'
        )
        
        JobSeekerProfile.objects.create(
            user=user,
            city='İstanbul',
            experience_years=3,
            skills='Saç kesimi, Boyama, Makyaj',
            bio='Test iş arayan profili',
            is_available=True
        )
        print("✅ Test job seeker oluşturuldu: test@jobseeker.com / test123")
    
    # Create test business
    if not User.objects.filter(email='test@business.com').exists():
        user = User.objects.create_user(
            username='test@business.com',
            email='test@business.com',
            password='test123',
            first_name='Test',
            last_name='Business',
            user_type='business'
        )
        
        BusinessProfile.objects.create(
            user=user,
            company_name='Test Güzellik Salonu',
            city='İstanbul',
            address='Test Mahallesi 1. Sokak No: 1',
            contact_phone='+905551234567',
            company_description='Test işletme profili'
        )
        print("✅ Test business oluşturuldu: test@business.com / test123")
        
        # Create test job listing
        if JobCategory.objects.exists():
            category = JobCategory.objects.first()
            JobListing.objects.create(
                business=user,
                title='Test Kuaför İş İlanı',
                description='Bu bir test iş ilanıdır. Deneyimli kuaför aranmaktadır.',
                category=category,
                city='İstanbul',
                salary_min=6000,
                salary_max=10000,
                is_urgent=True
            )
            print("✅ Test job listing oluşturuldu")
    
    print("🎉 Test veriler hazır!")

if __name__ == '__main__':
    create_test_data()
    
