# Generated by Django 5.0.1 on 2024-05-01 10:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0016_remove_event_user_club_user'),
        ('user', '0010_notification_event_notification_liked_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='favouriteuser',
            name='event_id',
            field=models.ForeignKey(db_column='event_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_id', to='club.event'),
        ),
        migrations.AddField(
            model_name='favouriteuser',
            name='status',
            field=models.BooleanField(null=True),
        ),
    ]
