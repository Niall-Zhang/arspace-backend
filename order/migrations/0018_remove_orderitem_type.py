# Generated by Django 5.0.4 on 2024-05-03 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0017_orderitem_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='type',
        ),
    ]
