# Generated by Django 5.0.4 on 2024-05-03 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0016_alter_order_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='type',
            field=models.CharField(choices=[('free', 'free')], default=None, max_length=15, null=True),
        ),
    ]
