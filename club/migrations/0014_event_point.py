# Generated by Django 4.2.9 on 2024-03-18 06:48

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0013_remove_eventticket_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='point',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
    ]
