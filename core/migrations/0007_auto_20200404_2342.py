# Generated by Django 2.2.12 on 2020-04-05 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20200404_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compra',
            name='moneda',
            field=models.CharField(choices=[('PYG', 'Guaraníes'), ('USD', 'Dólares')], default='PYG', max_length=3, verbose_name='Moneda'),
        ),
        migrations.AlterField(
            model_name='cuenta',
            name='moneda',
            field=models.CharField(choices=[('PYG', 'Guaraníes'), ('USD', 'Dólares')], default='PYG', max_length=3, verbose_name='Moneda'),
        ),
        migrations.AlterField(
            model_name='donacion',
            name='moneda',
            field=models.CharField(choices=[('PYG', 'Guaraníes'), ('USD', 'Dólares')], default='PYG', max_length=3, verbose_name='Moneda'),
        ),
    ]