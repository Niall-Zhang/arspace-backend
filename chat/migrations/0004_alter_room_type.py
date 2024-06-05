# Generated by Django 5.0.1 on 2024-05-01 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_room_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='type',
            field=models.CharField(choices=[('private', 'private'), ('group', 'group'), ('notification', 'notification')], max_length=15, null=True),
        ),
    ]