# Generated by Django 4.2.9 on 2024-01-31 11:04

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('club', '0003_event_latitude_event_longitude_likeevent'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LikeEvent',
            new_name='EventLike',
        ),
        migrations.RenameIndex(
            model_name='eventlike',
            new_name='event_like_uuid_9b2a45_idx',
            old_name='like_event_uuid_d0dfe7_idx',
        ),
        migrations.AlterModelTable(
            name='eventlike',
            table='event_like',
        ),
    ]
