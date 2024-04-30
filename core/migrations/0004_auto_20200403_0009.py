# Generated by Django 2.2.12 on 2020-04-03 04:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20200403_0008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concepto',
            name='padre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sub_conceptos', to='core.Concepto', verbose_name='Padre'),
        ),
    ]
