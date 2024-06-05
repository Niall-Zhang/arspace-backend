# Generated by Django 4.2.11 on 2024-03-13 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_remove_orderitem_qty_order_qty'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'pending'), ('completed', 'completed'), ('failed', 'failed'), ('refunded', 'refunded')], default='completed', max_length=15),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('valid', 'valid'), ('used', 'used'), ('expired', 'expired')], default='valid', max_length=15),
        ),
    ]
