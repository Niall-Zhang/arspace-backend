# Generated by Django 4.2.9 on 2024-02-01 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_order_gateway'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='qty',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
