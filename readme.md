# 🚀 Kuaför İlan - Hair Salon Job Platform

Modern, responsive ve kullanıcı dostu kuaför ve berber iş platformu. Django tabanlı, güvenli ve ölçeklenebilir bir sistem.

## ✨ Özellikler

### 🔐 Authentication
- **Multi-method Login**: Email/Password, OTP (SMS/Email)
- **Social Login**: Google, LinkedIn desteği
- **2FA Security**: OTP tabanlı doğrulama
- **Account Management**: Profil yönetimi, şifre sıfırlama

### 👥 User Management
- **Dual User Types**: İş Arayan (Job Seeker) ve İş Veren (Business)
- **Rich Profiles**: Detaylı profil bilgileri ve portfolyo desteği
- **Verification System**: Kimlik ve işletme doğrulama

### 💼 Job Management
- **Job Listings**: Kategorize edilmiş iş ilanları
- **Advanced Search**: Filtreleme ve arama sistemi
- **Application System**: Başvuru takip sistemi
- **Saved Jobs**: İlan kaydetme özelliği

### 📊 Dashboard & Analytics
- **Real-time Stats**: Anlık istatistikler
- **Interactive Charts**: Chart.js ile dinamik grafikler
- **Export Features**: PDF/Excel export
- **Activity Tracking**: Kullanıcı aktivite takibi

### 🛡️ Security Features
- **CSRF Protection**: Cross-site request forgery koruması
- **WordPress Bot Protection**: Otomatik bot engelleme
- **Rate Limiting**: API çağrı sınırlandırması
- **Input Validation**: Kapsamlı form doğrulaması

### 🎨 Modern UI/UX
- **Responsive Design**: Tüm cihazlarda uyumlu
- **LinkedIn-style Interface**: Modern ve tanıdık tasarım
- **Dark Mode Ready**: Koyu tema desteği hazır
- **PWA Compatible**: Progressive Web App hazırlığı

## 🛠️ Teknoloji Stack

### Backend
- **Framework**: Django 4.2.7
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **API**: Django REST Framework
- **Authentication**: Django Auth + Custom OTP

### Frontend
- **Templates**: Django Templates
- **CSS**: Custom CSS + Flexbox/Grid
- **JavaScript**: Vanilla JS + Chart.js
- **Icons**: Font Awesome

### Deployment
- **Platform**: Railway (Production)
- **Server**: Gunicorn + WhiteNoise
- **Database**: PostgreSQL (Railway)
- **CDN**: CloudFlare compatible

### External Services
- **SMS**: Netgsm API
- **Email**: Django Mail backend
- **File Storage**: Local + AWS S3 ready

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- pip
- virtualenv (önerilen)

### 1. Proje Klonlama
```bash
git clone https://github.com/mertekinci24/kuafor-ilan.git
cd kuafor-ilan
```

### 2. Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Bağımlılıkları Yükleme
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
`.env` dosyası oluşturun:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3

# SMS Settings (Optional)
NETGSM_USERNAME=your-netgsm-username
NETGSM_PASSWORD=your-netgsm-password
NETGSM_HEADER=KUAFORILAN

# Email Settings (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Admin Kullanıcı Oluşturma
```bash
python manage.py create_admin
```
Bu komut otomatik olarak admin kullanıcı oluşturur:
- **Email**: admin@kuaforilan.com
- **Şifre**: admin123

### 7. Test Verilerini Yükleme
```bash
python manage.py populate_categories
```

### 8. Sunucuyu Başlatma
```bash
python manage.py runserver
```

Site `http://127.0.0.1:8000` adresinde çalışacak.

## 📁 Proje Yapısı

```
kuafor_ilan/
├── apps/
│   ├── authentication/     # Kimlik doğrulama
│   ├── core/              # Temel modeller ve araçlar
│   ├── dashboard/         # Dashboard ve analytics
│   ├── jobs/              # İş ilanları sistemi
│   └── profiles/          # Kullanıcı profilleri
├── templates/             # HTML şablonları
│   ├── auth/             # Authentication sayfaları
│   ├── dashboard/        # Dashboard sayfaları
│   ├── jobs/             # İş ilanları sayfaları
│   └── profiles/         # Profil sayfaları
├── static/               # CSS, JS, resimler
├── media/                # Kullanıcı dosyaları
├── kuafor_ilan/         # Ana proje ayarları
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md
```

## 🔧 Kullanım

### Admin Panel
- URL: `/admin/`
- Giriş: admin@kuaforilan.com / admin123

### Ana Kullanıcı Tipleri

#### İş Arayan (Job Seeker)
- Profil oluşturma ve düzenleme
- İş ilanlarını görüntüleme ve filtreleme
- İş başvurusu yapma
- Başvuru takibi
- İlan kaydetme

#### İş Veren (Business)
- Şirket profili oluşturma
- İş ilanı verme
- Başvuruları inceleme
- Çalışan arama

### API Endpoints

#### Authentication
```
POST /auth/api/send-otp/        # OTP gönderme
POST /auth/api/verify-otp/      # OTP doğrulama
GET  /auth/login/               # Giriş sayfası
POST /auth/login/               # Giriş işlemi
GET  /auth/register/            # Kayıt sayfası
POST /auth/register/            # Kayıt işlemi
```

#### Jobs
```
GET  /jobs/                     # İş ilanları listesi
GET  /jobs/<id>/               # İş ilanı detayı
POST /jobs/<id>/apply/         # Başvuru yapma
```

#### Dashboard
```
GET  /dashboard/               # Dashboard ana sayfa
GET  /dashboard/api/stats/     # İstatistikler API
GET  /dashboard/api/chart-data/<period>/  # Chart verileri
```

## 🔒 Güvenlik

### Implemented Security Features
- CSRF token validation
- SQL injection protection
- XSS prevention
- WordPress bot protection
- Rate limiting ready
- Input sanitization
- Secure password hashing

### Environment Security
```env
# Production Settings
DEBUG=False
SECURE_SSL_REDIRECT=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 📱 Responsive Design

- **Mobile First**: Mobil cihazlar öncelikli tasarım
- **Breakpoints**: 480px, 768px, 1024px, 1200px
- **Touch Friendly**: Dokunmatik cihaz optimizasyonu
- **Fast Loading**: Optimized assets ve lazy loading

## 🚀 Production Deployment

### Railway Deployment
```bash
# Railway CLI kurulumu
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Environment Variables (Production)
```env
DEBUG=False
SECRET_KEY=production-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=secure-password
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
```

## 🔄 Migration & Updates

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files
```bash
python manage.py collectstatic --noinput
```

### Data Backup
```bash
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json
```

## 🐛 Troubleshooting

### Common Issues

#### Migration Errors
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

#### Static Files Not Loading
```bash
python manage.py collectstatic --clear
```

#### Admin User Issues
```bash
python manage.py create_admin  # Creates default admin
```

#### Database Reset
```bash
rm db.sqlite3
python manage.py migrate
python manage.py create_admin
```

## 📈 Performance Optimization

### Implemented Optimizations
- Database query optimization
- Static file compression
- Lazy loading for images
- Minified CSS/JS (production)
- CDN ready assets

### Future Optimizations
- Redis caching
- Database connection pooling
- Image optimization
- Content compression
- API caching

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- PEP 8 for Python code
- BEM methodology for CSS
- ESLint for JavaScript
- Django best practices

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Mert Ekinci**
- GitHub: [@mertekinci24](https://github.com/mertekinci24)
- Email: mert@example.com

## 🙏 Acknowledgments

- Django community for the excellent framework
- Chart.js for beautiful charts
- Font Awesome for icons
- Railway for hosting platform

## 📞 Support

Sorularınız için:
- GitHub Issues: [Create an issue](https://github.com/mertekinci24/kuafor-ilan/issues)
- Email: support@kuaforilan.com

---

⭐ Bu projeyi beğendiyseniz star vermeyi unutmayın!
