# Generated by Django 4.2.9 on 2024-03-19 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_notification_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notification',
            name='title',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('event', 'event'), ('room', 'room'), ('like', 'like')], max_length=15),
        ),
    ]