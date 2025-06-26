# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):
    initial = True
    
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'İş Kategorisi',
                'verbose_name_plural': 'İş Kategorileri',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='JobListing',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('requirements', models.TextField(blank=True)),
                ('salary_min', models.PositiveIntegerField(blank=True, null=True)),
                ('salary_max', models.PositiveIntegerField(blank=True, null=True)),
                ('salary_type', models.CharField(choices=[('hourly', 'Saatlik'), ('daily', 'Günlük'), ('monthly', 'Aylık'), ('yearly', 'Yıllık'), ('project', 'Proje Bazlı')], default='monthly', max_length=20)),
                ('location', models.CharField(max_length=200)),
                ('remote_work', models.BooleanField(default=False)),
                ('experience_level', models.CharField(choices=[('entry', 'Giriş Seviyesi'), ('junior', 'Junior'), ('mid', 'Orta'), ('senior', 'Senior'), ('expert', 'Uzman')], default='entry', max_length=20)),
                ('employment_type', models.CharField(choices=[('full_time', 'Tam Zamanlı'), ('part_time', 'Yarı Zamanlı'), ('contract', 'Sözleşmeli'), ('freelance', 'Serbest'), ('internship', 'Staj')], default='full_time', max_length=20)),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('draft', 'Taslak'), ('active', 'Aktif'), ('paused', 'Duraklatıldı'), ('closed', 'Kapatıldı'), ('filled', 'Dolduruldu')], default='draft', max_length=20)),
                ('is_featured', models.BooleanField(default=False)),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('applications_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_listings', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_listings', to='jobs.jobcategory')),
            ],
            options={
                'verbose_name': 'İş İlanı',
                'verbose_name_plural': 'İş İlanları',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('cover_letter', models.TextField(blank=True)),
                ('resume', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('status', models.CharField(choices=[('pending', 'Beklemede'), ('reviewing', 'İnceleniyor'), ('shortlisted', 'Kısa Liste'), ('interview', 'Mülakat'), ('hired', 'İşe Alındı'), ('rejected', 'Reddedildi')], default='pending', max_length=20)),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_applications', to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='jobs.joblisting')),
            ],
            options={
                'verbose_name': 'İş Başvurusu',
                'verbose_name_plural': 'İş Başvuruları',
                'ordering': ['-applied_at'],
                'unique_together': {('applicant', 'job')},
            },
        ),
        migrations.CreateModel(
            name='SavedJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_by', to='jobs.joblisting')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_jobs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Kaydedilen İş',
                'verbose_name_plural': 'Kaydedilen İşler',
                'unique_together': {('user', 'job')},
            },
        ),
        migrations.CreateModel(
            name='JobView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_views', to='jobs.joblisting')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='job_views', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'İş İlanı Görüntülenmesi',
                'verbose_name_plural': 'İş İlanı Görüntülenmeleri',
                'ordering': ['-viewed_at'],
            },
        ),
    ]
  
