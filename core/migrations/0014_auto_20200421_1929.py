# Generated by Django 2.2.12 on 2020-04-21 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20200415_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donacion',
            name='nro_comprobante',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Comprobante Nro.'),
        ),
    ]