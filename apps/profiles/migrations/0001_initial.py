# Generated manually
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
            name='JobSeekerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('full_name', models.CharField(max_length=100)),
                ('bio', models.TextField(blank=True)),
                ('experience_years', models.PositiveIntegerField(default=0)),
                ('skills', models.TextField(blank=True, help_text='Yetenekler virgül ile ayrılsın')),
                ('portfolio_images', models.TextField(blank=True, help_text='Fotoğraf URL\'leri')),
                ('city', models.CharField(max_length=50)),
                ('district', models.CharField(blank=True, max_length=50)),
                ('is_available', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='job_seeker_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'İş Arayan Profili',
                'verbose_name_plural': 'İş Arayan Profilleri',
            },
        ),
        migrations.CreateModel(
            name='BusinessProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business_name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=50)),
                ('district', models.CharField(blank=True, max_length=50)),
                ('phone', models.CharField(max_length=15)),
                ('website', models.URLField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='business_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'İş Veren Profili',
                'verbose_name_plural': 'İş Veren Profilleri',
            },
        ),
    ]
  
