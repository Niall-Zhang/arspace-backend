# Generated by Django 5.0.2 on 2024-02-09 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_chatrequest_is_sent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatrequest',
            name='is_sent',
        ),
    ]