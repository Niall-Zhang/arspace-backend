# Generated by Django 4.2.9 on 2024-02-14 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_remove_chatrequest_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercard',
            name='card_token',
            field=models.CharField(max_length=35),
        ),
    ]