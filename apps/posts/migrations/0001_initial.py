from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Kategori Adı')),
                ('slug', models.SlugField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
                ('icon', models.CharField(blank=True, max_length=50, verbose_name='İkon')),
                ('color', models.CharField(default='#0a66c2', max_length=7, verbose_name='Renk')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
            ],
            options={
                'verbose_name': 'Post Kategorisi',
                'verbose_name_plural': 'Post Kategorileri',
                'ordering': ['name'],
            },
        ),
        # Diğer modeller...
    ]
    
