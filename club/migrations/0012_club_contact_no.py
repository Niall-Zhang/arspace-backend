# Generated by Django 4.2.9 on 2024-02-16 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0011_event_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='contact_no',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
