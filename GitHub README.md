# 🚀 Kuaför İlan Platformu

Modern, kullanıcı dostu kuaför ve güzellik sektörü iş bulma platformu.

![Platform Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Django](https://img.shields.io/badge/Django-4.2.7-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📖 Proje Hakkında

Kuaför İlan Platformu, güzellik sektöründe çalışan profesyoneller ile işverenleri buluşturan modern bir web platformudur. LinkedIn tarzı kullanıcı deneyimi ile geliştirilmiştir.

### ✨ Temel Özellikler

- 🔐 **Güvenli Authentication**: OTP destekli giriş sistemi
- 👥 **Dual Profile System**: İş arayan ve işveren profilleri
- 💼 **Akıllı İş Eşleştirme**: Kategori bazlı filtreleme
- 📊 **Canlı Dashboard**: Gerçek zamanlı istatistikler
- 📱 **Responsive Design**: Mobil uyumlu arayüz
- 🔍 **Gelişmiş Arama**: Multi-filter arama sistemi

## 🚀 Hızlı Başlangıç

### Ön Gereksinimler
- Python 3.11+
- Django 4.2.7
- PostgreSQL (opsiyonel)

### Kurulum

```bash
# Projeyi klonlayın
git clone https://github.com/username/kuafor-ilan.git
cd kuafor-ilan

# Otomatik kurulum
bash setup.sh

# Veya manuel kurulum
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py create_admin
python manage.py runserver
```

### Demo Veriler

```bash
# Test verilerini yükle
python manage.py create_sample_data --users 20 --jobs 50

# Test kullanıcıları
# İş Arayan: test@jobseeker.com / test123
# İşveren: test@business.com / test123
# Admin: admin@kuaforilan.com / admin123
```

## 🛠️ Teknoloji Stack

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework** - API geliştirme
- **PostgreSQL** - Veritabanı
- **Redis** - Cache ve session storage
- **Celery** - Asenkron görevler

### Frontend
- **Bootstrap 5** - UI framework
- **Chart.js** - Data visualization
- **Vanilla JavaScript** - Interaktivite
- **SCSS** - Styling

### Deployment
- **Docker** - Containerization
- **Nginx** - Web server
- **Gunicorn** - WSGI server
- **Railway/Heroku** - Cloud deployment

## 📊 Proje Durumu

### ✅ Tamamlanan Özellikler (85%)
- Authentication & Authorization
- Profile Management
- Job Listings & Applications
- Search & Filtering
- Dashboard & Analytics
- Email/SMS Notifications

### 🔄 Geliştirme Aşamasında (15%)
- Job Creation Interface
- Advanced Messaging System
- Payment Integration
- Mobile App

Detaylı durum için: [PROJECT_STATUS.md](docs/PROJECT_STATUS.md)

## 📱 Demo & Screenshots

### 🌐 **Live Demo**: [kuafor-ilan.railway.app](https://kuafor-ilan.railway.app)

### 📸 **Screenshots**

| Ana Sayfa | Dashboard | İş İlanları |
|-----------|-----------|-------------|
| ![Home](screenshots/home.png) | ![Dashboard](screenshots/dashboard.png) | ![Jobs](screenshots/jobs.png) |

## 🚀 Development

### Geliştirme Komutları

```bash
# Development server
bash dev_commands.sh run

# Database reset
bash dev_commands.sh reset-db

# Test çalıştırma
bash dev_commands.sh test

# Static files toplama
bash dev_commands.sh collect
```

### Docker ile Geliştirme

```bash
# Development environment
docker-compose up -d

# Production build
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing

```bash
# Unit testler
python manage.py test

# Coverage report
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🚀 Deployment

### Railway (Önerilen)
```bash
# Railway CLI kurulumu
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Heroku
```bash
# Heroku CLI kurulumu sonrası
heroku create kuafor-ilan
git push heroku main
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

Detaylı deployment rehberi: [DEPLOYMENT.md](docs/DEPLOYMENT.md)

## 📚 Dokümantasyon

- [🗺️ Development Roadmap](ROADMAP.md)
- [📊 Proje Durumu](docs/PROJECT_STATUS.md)
- [🔧 Development Guide](docs/DEVELOPMENT_GUIDE.md)
- [🚀 Deployment Guide](docs/DEPLOYMENT.md)
- [🤝 Contributing Guide](CONTRIBUTING.md)

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 License

Bu proje MIT License altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👥 Team

- **Lead Developer**: [Your Name](https://github.com/yourusername)
- **UI/UX Designer**: [Designer Name](https://github.com/designer)
- **Backend Developer**: [Developer Name](https://github.com/developer)

## 📞 İletişim

- **Email**: info@kuaforilan.com
- **LinkedIn**: [Kuaför İlan](https://linkedin.com/company/kuaforilan)
- **Website**: [kuaforilan.com](https://kuaforilan.com)

---

⭐ Bu projeyi beğendiyseniz star vermeyi unutmayın!

[![GitHub stars](https://img.shields.io/github/stars/username/kuafor-ilan.svg?style=social&label=Star)](https://github.com/username/kuafor-ilan)
