from django.db import migrations, models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='E-posta')),
                ('phone', models.CharField(blank=True, max_length=15, verbose_name='Telefon')),
                ('user_type', models.CharField(choices=[('jobseeker', 'İş Arayan'), ('business', 'İş Veren')], default='jobseeker', max_length=20, verbose_name='Kullanıcı Tipi')),
                ('current_plan', models.CharField(choices=[('free', 'Ücretsiz'), ('pro', 'Pro'), ('business', 'İşletme')], default='free', max_length=20, verbose_name='Mevcut Plan')),
                ('plan_start_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Plan Başlangıç')),
                ('plan_end_date', models.DateTimeField(blank=True, null=True, verbose_name='Plan Bitiş')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Doğrulanmış')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')),
                ('profile_views', models.IntegerField(default=0, verbose_name='Profil Görüntülenme')),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='Son Giriş IP')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Kullanıcı',
                'verbose_name_plural': 'Kullanıcılar',
                'db_table': 'auth_users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='JobSeekerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Doğum Tarihi')),
                ('city', models.CharField(max_length=50, verbose_name='Şehir')),
                ('district', models.CharField(blank=True, max_length=50, verbose_name='İlçe')),
                ('address', models.TextField(blank=True, verbose_name='Adres')),
                ('experience_years', models.CharField(choices=[('beginner', 'Yeni başlayan'), ('1-2', '1-2 yıl'), ('3-5', '3-5 yıl'), ('6-10', '6-10 yıl'), ('10+', '10+ yıl')], default='beginner', max_length=20, verbose_name='Deneyim')),
                ('skills', models.JSONField(default=list, verbose_name='Yetenekler')),
                ('bio', models.TextField(blank=True, verbose_name='Hakkında')),
                ('portfolio_url', models.URLField(blank=True, verbose_name='Portföy URL')),
                ('cv_file', models.FileField(blank=True, upload_to='cvs/', verbose_name='CV Dosyası')),
                ('certificates', models.JSONField(default=list, verbose_name='Sertifikalar')),
                ('total_applications', models.IntegerField(default=0, verbose_name='Toplam Başvuru')),
                ('successful_applications', models.IntegerField(default=0, verbose_name='Başarılı Başvuru')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='jobseeker_profile', to='authentication.customuser')),
            ],
            options={
                'verbose_name': 'İş Arayan Profili',
                'verbose_name_plural': 'İş Arayan Profilleri',
                'db_table': 'jobseeker_profiles',
            },
        ),
        migrations.CreateModel(
            name='BusinessProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200, verbose_name='Şirket Adı')),
                ('company_description', models.TextField(blank=True, verbose_name='Şirket Açıklaması')),
                ('company_size', models.CharField(choices=[('1-5', '1-5 kişi'), ('6-20', '6-20 kişi'), ('21-50', '21-50 kişi'), ('51-100', '51-100 kişi'), ('100+', '100+ kişi')], max_length=20, verbose_name='Şirket Büyüklüğü')),
                ('establishment_year', models.IntegerField(verbose_name='Kuruluş Yılı')),
                ('city', models.CharField(max_length=50, verbose_name='Şehir')),
                ('district', models.CharField(blank=True, max_length=50, verbose_name='İlçe')),
                ('address', models.TextField(verbose_name='Adres')),
                ('website', models.URLField(blank=True, verbose_name='Web Sitesi')),
                ('contact_person', models.CharField(max_length=100, verbose_name='Yetkili Kişi')),
                ('contact_phone', models.CharField(max_length=15, verbose_name='Yetkili Telefon')),
                ('total_job_posts', models.IntegerField(default=0, verbose_name='Toplam İlan')),
                ('active_job_posts', models.IntegerField(default=0, verbose_name='Aktif İlan')),
                ('total_applications_received', models.IntegerField(default=0, verbose_name='Alınan Başvuru')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Doğrulanmış Şirket')),
                ('verification_documents', models.JSONField(default=list, verbose_name='Doğrulama Belgeleri')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='business_profile', to='authentication.customuser')),
            ],
            options={
                'verbose_name': 'İş Veren Profili',
                'verbose_name_plural': 'İş Veren Profilleri',
                'db_table': 'business_profiles',
            },
        ),
    ]
  
