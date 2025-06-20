# Railway specific settings
import os
if 'RAILWAY_ENVIRONMENT' in os.environ:
    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = [
        'https://*.railway.app',
        'https://kuaforilan.com',
        'https://www.kuaforilan.com'
    ]
    CORS_ALLOW_ALL_ORIGINS = True
    SECURE_SSL_REDIRECT = False  # Railway handles SSL
