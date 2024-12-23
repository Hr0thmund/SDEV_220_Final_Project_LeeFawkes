# Generated by Django 5.1.4 on 2024-12-14 23:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('configurator', '0005_remove_card_port_index_modularplatform_port_index'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='card',
            unique_together={('brand', 'model', 'revision')},
        ),
        migrations.AlterUniqueTogether(
            name='platform',
            unique_together={('brand', 'model', 'revision')},
        ),
    ]
