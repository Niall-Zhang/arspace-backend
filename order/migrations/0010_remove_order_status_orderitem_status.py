# Generated by Django 4.2.11 on 2024-03-13 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_order_payment_status_alter_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='status',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('valid', 'valid'), ('used', 'used'), ('expired', 'expired')], default='valid', max_length=15),
        ),
    ]