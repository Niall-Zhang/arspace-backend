# Generated by Django 4.2.9 on 2024-03-11 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_alter_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='qty',
        ),
        migrations.AddField(
            model_name='order',
            name='qty',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
