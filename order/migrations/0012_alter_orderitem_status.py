# Generated by Django 4.2.11 on 2024-03-13 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_alter_orderitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('verified', 'verified'), ('not_verified', 'not_verified'), ('expired', 'expired')], default='not_verified', max_length=15),
        ),
    ]
