# Generated by Django 5.0.2 on 2024-02-09 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatrequest',
            name='is_sent',
            field=models.BooleanField(default=False),
        ),
    ]
