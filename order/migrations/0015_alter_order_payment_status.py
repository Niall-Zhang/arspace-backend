# Generated by Django 5.0.4 on 2024-05-03 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_order_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'pending'), ('completed', 'completed'), ('failed', 'failed'), ('refunded', 'refunded')], default='completed', max_length=15, null=True),
        ),
    ]
