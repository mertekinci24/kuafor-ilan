# Generated by Django 4.2.8 on 2025-06-27 23:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(choices=[('job_application', 'İş Başvurusu'), ('job_application_status', 'Başvuru Durumu Değişikliği'), ('new_job_match', 'Uygun İş İlanı'), ('job_deadline', 'İlan Son Başvuru Tarihi'), ('new_message', 'Yeni Mesaj'), ('message_read', 'Mesaj Okundu'), ('post_like', 'Gönderi Beğenisi'), ('post_comment', 'Gönderi Yorumu'), ('post_share', 'Gönderi Paylaşımı'), ('new_follower', 'Yeni Takipçi'), ('system_update', 'Sistem Güncellemesi'), ('account_security', 'Hesap Güvenliği'), ('profile_incomplete', 'Profil Eksiklikleri'), ('verification_status', 'Doğrulama Durumu'), ('new_application', 'Yeni Başvuru'), ('application_deadline', 'Başvuru Süresi Bitiyor'), ('profile_view', 'Profil Görüntülendi'), ('promotion', 'Promosyon'), ('newsletter', 'Haber Bülteni'), ('event_reminder', 'Etkinlik Hatırlatması')], max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(default='fas fa-bell', max_length=50)),
                ('color', models.CharField(default='#007bff', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
                ('send_email', models.BooleanField(default=False)),
                ('send_sms', models.BooleanField(default=False)),
                ('send_push', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Bildirim Türü',
                'verbose_name_plural': 'Bildirim Türleri',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserNotificationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_notifications', models.BooleanField(default=True)),
                ('sms_notifications', models.BooleanField(default=False)),
                ('push_notifications', models.BooleanField(default=True)),
                ('job_applications', models.BooleanField(default=True)),
                ('job_matches', models.BooleanField(default=True)),
                ('job_deadlines', models.BooleanField(default=True)),
                ('new_messages', models.BooleanField(default=True)),
                ('message_read_receipts', models.BooleanField(default=False)),
                ('post_interactions', models.BooleanField(default=True)),
                ('new_followers', models.BooleanField(default=True)),
                ('system_updates', models.BooleanField(default=True)),
                ('security_alerts', models.BooleanField(default=True)),
                ('promotions', models.BooleanField(default=False)),
                ('newsletters', models.BooleanField(default=False)),
                ('quiet_hours_enabled', models.BooleanField(default=False)),
                ('quiet_hours_start', models.TimeField(default='22:00')),
                ('quiet_hours_end', models.TimeField(default='08:00')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Kullanıcı Bildirim Ayarları',
                'verbose_name_plural': 'Kullanıcı Bildirim Ayarları',
            },
        ),
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('title_template', models.CharField(max_length=200)),
                ('message_template', models.TextField()),
                ('email_subject_template', models.CharField(blank=True, max_length=200)),
                ('email_body_template', models.TextField(blank=True)),
                ('sms_template', models.CharField(blank=True, max_length=160)),
                ('variables', models.JSONField(blank=True, default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notification_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='templates', to='notifications.notificationtype')),
            ],
            options={
                'verbose_name': 'Bildirim Şablonu',
                'verbose_name_plural': 'Bildirim Şablonları',
            },
        ),
        migrations.CreateModel(
            name='NotificationBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('recipient_filter', models.JSONField(default=dict)),
                ('total_recipients', models.PositiveIntegerField(default=0)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('action_url', models.URLField(blank=True)),
                ('action_text', models.CharField(blank=True, max_length=50)),
                ('is_sent', models.BooleanField(default=False)),
                ('sent_count', models.PositiveIntegerField(default=0)),
                ('failed_count', models.PositiveIntegerField(default=0)),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_notification_batches', to=settings.AUTH_USER_MODEL)),
                ('notification_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.notificationtype')),
            ],
            options={
                'verbose_name': 'Toplu Bildirim',
                'verbose_name_plural': 'Toplu Bildirimler',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('short_message', models.CharField(blank=True, max_length=100)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('priority', models.CharField(choices=[('low', 'Düşük'), ('normal', 'Normal'), ('high', 'Yüksek'), ('urgent', 'Acil')], default='normal', max_length=10)),
                ('action_url', models.URLField(blank=True, null=True)),
                ('action_text', models.CharField(blank=True, max_length=50)),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('is_sent', models.BooleanField(default=False)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('is_delivered', models.BooleanField(default=False)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('email_sent', models.BooleanField(default=False)),
                ('email_sent_at', models.DateTimeField(blank=True, null=True)),
                ('sms_sent', models.BooleanField(default=False)),
                ('sms_sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('notification_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.notificationtype')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bildirim',
                'verbose_name_plural': 'Bildirimler',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['recipient', 'is_read'], name='notificatio_recipie_4e3567_idx'), models.Index(fields=['recipient', 'created_at'], name='notificatio_recipie_f39341_idx'), models.Index(fields=['notification_type', 'created_at'], name='notificatio_notific_5e6e57_idx')],
            },
        ),
    ]
