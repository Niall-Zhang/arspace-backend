# Generated by Django 4.2.9 on 2024-03-19 07:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]