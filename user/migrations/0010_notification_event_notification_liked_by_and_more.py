# Generated by Django 4.2.9 on 2024-03-19 08:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0015_alter_event_location'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0003_room_type'),
        ('user', '0009_alter_notification_status_alter_notification_title_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='club.event'),
        ),
        migrations.AddField(
            model_name='notification',
            name='liked_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='liked_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notification',
            name='room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chat.room'),
        ),
    ]