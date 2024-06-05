# Generated by Django 4.2.9 on 2024-01-31 06:37

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
            name='Cast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(db_index=True, max_length=50, unique=True)),
                ('description', models.TextField(null=True)),
                ('image', models.ImageField(null=True, upload_to='casts')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'casts',
            },
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(db_index=True, max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'clubs',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(db_index=True, max_length=50, unique=True)),
                ('description', models.TextField(null=True)),
                ('early_bird_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('adult_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('children_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('date', models.DateField(blank=True, null=True)),
                ('time', models.TimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'club_events',
            },
        ),
        migrations.CreateModel(
            name='EventImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('image', models.ImageField(null=True, upload_to='events')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.event')),
            ],
            options={
                'db_table': 'event_images',
                'indexes': [models.Index(fields=['uuid'], name='event_image_uuid_62c9fe_idx')],
            },
        ),
        migrations.CreateModel(
            name='EventCast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('cast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.cast')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.event')),
            ],
            options={
                'db_table': 'event_casts',
                'indexes': [models.Index(fields=['uuid'], name='event_casts_uuid_e042ca_idx')],
            },
        ),
    ]
