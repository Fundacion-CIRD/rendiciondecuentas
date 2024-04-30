# Generated by Django 2.2.12 on 2020-04-03 03:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('utils', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(verbose_name='fecha')),
                ('nro_timbrado', models.IntegerField(blank=True, null=True, verbose_name='Timbrado Nro.')),
                ('nro_comprobante', models.CharField(max_length=50, verbose_name='Comprobante Nro.')),
                ('nro_orden_pago', models.CharField(max_length=50, verbose_name='Orden de Pago Nro.')),
            ],
            options={
                'verbose_name': 'Adquisición Realizada/Destino',
                'verbose_name_plural': 'Adquisiciones Realizadas/Destinos',
                'ordering': ('-fecha',),
            },
        ),
        migrations.CreateModel(
            name='Concepto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, default='', verbose_name='Descripción')),
                ('medida', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='utils.UnidadMedida', verbose_name='Unidad de Medida')),
                ('padre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sub_conceptos', to='core.Concepto', verbose_name='Padre')),
            ],
            options={
                'verbose_name': 'Concepto',
                'verbose_name_plural': 'Conceptos',
                'ordering': ('nombre',),
            },
        ),
        migrations.CreateModel(
            name='Cuenta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nro', models.CharField(max_length=50, verbose_name='Cuenta Nro.')),
            ],
            options={
                'verbose_name': 'Cuenta',
                'verbose_name_plural': 'Cuentas',
                'ordering': ('entidad',),
            },
        ),
        migrations.CreateModel(
            name='Entidad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(db_index=True, max_length=254, verbose_name='nombre')),
                ('info_extra', models.TextField(blank=True, default='', verbose_name='Información Adicional')),
            ],
            options={
                'verbose_name': 'Entidad',
                'verbose_name_plural': 'Entidades',
                'ordering': ('nombre',),
            },
        ),
        migrations.CreateModel(
            name='TipoComprobante',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Tipo de Comprobante',
                'verbose_name_plural': 'Tipos de Comprobante',
            },
        ),
        migrations.CreateModel(
            name='TipoCuenta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Tipo de Cuenta',
                'verbose_name_plural': 'Tipos de Cuenta',
            },
        ),
        migrations.CreateModel(
            name='ItemCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.FloatField(verbose_name='Cantidad')),
                ('precio_unitario', models.FloatField(verbose_name='Precio Unitario')),
                ('precio_total', models.FloatField(verbose_name='Precio Total')),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='core.Compra', verbose_name='Compra')),
                ('concepto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.Concepto', verbose_name='Concepto')),
                ('moneda', models.ForeignKey(default='PYG', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='utils.Moneda', verbose_name='moneda')),
            ],
            options={
                'verbose_name': 'Item',
                'verbose_name_plural': 'Items',
            },
        ),
        migrations.CreateModel(
            name='Donacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(verbose_name='fecha')),
                ('nro_comprobante', models.CharField(max_length=50, verbose_name='Comprobante Nro.')),
                ('recibo_nro', models.IntegerField(blank=True, null=True, verbose_name='Recibo de Donación Nro.')),
                ('monto', models.FloatField(verbose_name='Monto')),
                ('es_anonimo', models.BooleanField(default=True, help_text='Desmarcar la casilla si el donante desea que su nombre aparezca en la web', verbose_name='Donante Anonimo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cuenta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ingresos', to='core.Cuenta', verbose_name='cuenta')),
                ('donante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.Entidad', verbose_name='nombre')),
                ('moneda', models.ForeignKey(default='PYG', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='utils.Moneda', verbose_name='Moneda')),
            ],
            options={
                'verbose_name': 'Donación Recibida',
                'verbose_name_plural': 'Donaciones Recibidas',
                'ordering': ('-fecha',),
            },
        ),
        migrations.AddField(
            model_name='cuenta',
            name='entidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.Entidad', verbose_name='Entidad'),
        ),
        migrations.AddField(
            model_name='cuenta',
            name='moneda',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='utils.Moneda', verbose_name='Moneda'),
        ),
        migrations.AddField(
            model_name='cuenta',
            name='tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cuentas', to='core.TipoCuenta', verbose_name='Tipo de Cuenta'),
        ),
        migrations.AddField(
            model_name='compra',
            name='proveedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.Entidad', verbose_name='Proveedor/Oferente'),
        ),
        migrations.AddField(
            model_name='compra',
            name='tipo_comprobante',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='core.TipoComprobante', verbose_name='Tipo de Comprobante'),
        ),
    ]
