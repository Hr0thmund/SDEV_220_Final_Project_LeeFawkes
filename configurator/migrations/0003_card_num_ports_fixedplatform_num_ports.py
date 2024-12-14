# Generated by Django 5.1.4 on 2024-12-14 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configurator', '0002_remove_slotinventory_modular_platform'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='num_ports',
            field=models.IntegerField(default=36),
        ),
        migrations.AddField(
            model_name='fixedplatform',
            name='num_ports',
            field=models.IntegerField(default=48),
        ),
    ]
