# Generated by Django 4.2.5 on 2025-05-30 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vortex_logistics_app', '0007_alter_delivery_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='status',
            field=models.CharField(blank=True, choices=[('Ordered', 'Ordered'), ('Picked', 'Picked'), ('In-Transist', 'In-Transist'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')], max_length=25, null=True),
        ),
    ]
