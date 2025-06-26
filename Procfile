release: python manage.py makemigrations && python manage.py migrate
web: python manage.py collectstatic --noinput && gunicorn kuafor_ilan.wsgi:application
