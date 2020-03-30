from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.datetime_safe import strftime


class Entidad(models.Model):
    nombre = models.CharField(max_length=254, db_index=True, verbose_name='nombre')
    info_extra = models.TextField(default='', blank=True, verbose_name='Información Adicional')

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'Entidad'
        verbose_name_plural = 'Entidades'

    def __str__(self):
        return self.nombre


class Cuenta(models.Model):
    CTA_CTE = 'banco_cta_cte'
    CAJA_AHORRO = 'banco_caja_ahorro'
    GIRO = 'giro'
    TIPO_CHOICES = (
        (CTA_CTE, 'Cuenta Corriente'),
        (CAJA_AHORRO, 'Caja de Ahorro'),
        (GIRO, 'Giro bancario')
    )
    entidad = models.ForeignKey(Entidad, on_delete=models.PROTECT, related_name='+', verbose_name='Entidad')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name='tipo')
    nro = models.CharField(max_length=50, verbose_name='Cuenta Nro.')

    class Meta:
        ordering = ('entidad',)
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'

    def __str__(self):
        return '{}: {} {}'.format(self.entidad.nombre, self.get_tipo_display(), self.nro)


class Cambio(models.Model):
    USD = 'USD'
    MONEDA_CHOICES = ((USD, 'Dólares Americanos'),)
    fecha = models.DateField(verbose_name='fecha')
    cambio = models.FloatField(verbose_name='cambio')
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default=USD, verbose_name='moneda')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-fecha',)
        verbose_name = 'Cambio'
        verbose_name_plural = 'Cambios'

    def __str__(self):
        fecha_str = strftime(self.fecha, '%d/%m/%Y')
        return '{} {}'.format(fecha_str, self.cambio)


class Documento(models.Model):
    archivo = models.FileField(upload_to='documentos', verbose_name='Archivo')
    descripcion = models.TextField(default='', blank=True, verbose_name='Descripción')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        if len(self.descripcion) > 20:
            return '{}...'.format(self.descripcion[:17])
        return self.descripcion


class Donacion(models.Model):
    fecha = models.DateField(verbose_name='fecha')
    origen = models.ForeignKey(Entidad, on_delete=models.PROTECT, related_name='+', verbose_name='origen')
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name='ingresos', verbose_name='cuenta')
    nro_comprobante = models.CharField(max_length=50, verbose_name='Comprobante Nro.')
    recibo_nro = models.IntegerField(verbose_name='Recibo de Donación Nro.')
    monto_pyg = models.FloatField(null=True, blank=True, verbose_name='Monto Gs.')
    monto_usd = models.FloatField(null=True, blank=True, verbose_name='Monto USD')
    es_anonimo = models.BooleanField(default=False, verbose_name='Publicar como donación anónima')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-fecha',)
        verbose_name = 'Donación'
        verbose_name_plural = 'Donaciones'

    def __str__(self):
        # fecha_str = strftime(self.fecha, '%d/%m/%Y')
        return '{} ({})'.format(self.origen, self.fecha)

    def clean(self):
        if self.monto_pyg and self.monto_usd:
            raise ValidationError('No se permiten montos en Gs. y USD al mismo tiempo.')


class Compra(models.Model):
    FACTURA = 1
    RECIBO = 2
    TIPO_COMPROBANTE_CHOICES = (
        (FACTURA, 'Factura'),
        (RECIBO, 'Recibo Legal'),
    )
    fecha = models.DateField(verbose_name='fecha')
    proveedor = models.ForeignKey(Entidad, on_delete=models.PROTECT, related_name='+', verbose_name='Proveedor/Oferente')
    tipo_comprobante = models.IntegerField(choices=TIPO_COMPROBANTE_CHOICES, verbose_name='Tipo de Comprobante')
    nro_timbrado = models.IntegerField(null=True, blank=True, verbose_name='Timbrado Nro.')
    nro_comprobante = models.CharField(max_length=50, verbose_name='Comprobante Nro.')
    nro_op = models.CharField(max_length=50, verbose_name='O.P. Nro.')
    concepto = models.CharField(max_length=254, verbose_name='Concepto')
    cantidad = models.FloatField(verbose_name='Cantidad')
    precio_unidad_pyg = models.FloatField(null=True, blank=True, verbose_name='Precio unitario Gs.')
    precio_total_pyg = models.FloatField(null=True, blank=True, verbose_name='Precio total Gs.')
    precio_unidad_usd = models.FloatField(null=True, blank=True, verbose_name='Precio unitario USD.')
    precio_total_usd = models.FloatField(null=True, blank=True, verbose_name='Precio total USD.')
    beneficiario = models.ForeignKey(
        Entidad, on_delete=models.PROTECT, related_name='+', verbose_name=('Institución Beneficiada'),
        help_text='A qué establecimiento se entregó la donación')
    recepcion_donacion = models.CharField(
        max_length=254, verbose_name='Recepción de la Donación', help_text='Quién recibió la donación')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-fecha',)
        verbose_name = 'Compra/Destino de la donación'
        verbose_name_plural = 'Compras/Destino de las donaciones'

    def __str__(self):
        # fecha_str = strftime(self.fecha, '%d/%m/%Y')
        return '{} - {}'.format(self.fecha, self.proveedor)

    def clean(self):
        if (self.precio_unidad_pyg or self.precio_total_usd) and (self.precio_unidad_usd or self.precio_total_usd):
            raise ValidationError('No se permiten montos en Gs. y USD al mismo tiempo.')
        if self.precio_unidad_pyg and not self.precio_total_pyg or not self.precio_unidad_pyg and self.precio_total_pyg:
            raise ValidationError('Debe cargar precio unitario y precio total.')
        if self.precio_unidad_usd and not self.precio_total_usd or not self.precio_unidad_usd and self.precio_total_usd:
            raise ValidationError('Debe cargar precio unitario y precio total.')
        if self.precio_unidad_usd and not self.precio_total_usd == self.precio_unidad_usd * self.cantidad:
            raise ValidationError('El precio total no coincide con el producto de Precio Unitario x Cantidad')
        if self.precio_unidad_pyg and not self.precio_total_pyg == self.precio_unidad_pyg * self.cantidad:
            raise ValidationError('El precio total no coincide con el producto de Precio Unitario x Cantidad')
