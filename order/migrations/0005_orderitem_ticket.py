# Generated by Django 4.2.9 on 2024-02-16 04:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0010_rename_unit_eventticket_units'),
        ('order', '0004_remove_orderitem_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='ticket',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='club.eventticket'),
        ),
    ]