# Generated by Django 2.2.12 on 2020-04-05 03:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0003_auto_20200403_0004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tipocambio',
            name='moneda',
        ),
        migrations.DeleteModel(
            name='Moneda',
        ),
    ]
