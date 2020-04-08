from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from utils.models import UnidadMedida, TipoCambio
from utils.constants import PYG, MONEDA_CHOICES


class Entidad(models.Model):
    nombre = models.CharField(max_length=254, db_index=True, verbose_name='nombre')
    info_extra = models.TextField(default='', blank=True, verbose_name='Información Adicional')

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'Entidad'
        verbose_name_plural = 'Entidades'

    def __str__(self):
        return self.nombre


class TipoCuenta(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')

    class Meta:
        verbose_name = 'Tipo de Cuenta'
        verbose_name_plural = 'Tipos de Cuenta'

    def __str__(self):
        return self.nombre


class Cuenta(models.Model):
    entidad = models.ForeignKey(Entidad, on_delete=models.PROTECT, related_name='+', verbose_name='Entidad')
    tipo = models.ForeignKey(
        TipoCuenta, on_delete=models.PROTECT, related_name='cuentas', verbose_name='Tipo de Cuenta')
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default=PYG, verbose_name='Moneda')
    nro = models.CharField(max_length=50, verbose_name='Cuenta Nro.')

    class Meta:
        ordering = ('entidad',)
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'

    def __str__(self):
        return '{}: {} {} {}'.format(self.entidad.nombre, self.tipo.nombre, self.get_moneda_display(), self.nro)


class Donacion(models.Model):
    fecha = models.DateField(verbose_name='fecha')
    donante = models.ForeignKey(Entidad, on_delete=models.PROTECT, related_name='+', verbose_name='nombre')
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name='ingresos', verbose_name='cuenta')
    nro_comprobante = models.CharField(max_length=50, verbose_name='Comprobante Nro.')
    recibo_nro = models.IntegerField(null=True, blank=True, verbose_name='Recibo de Donación Nro.')
    monto = models.FloatField(verbose_name='Monto')
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default=PYG, verbose_name='Moneda')
    es_anonimo = models.BooleanField(
        default=True, verbose_name='Donante Anonimo',
        help_text='Desmarcar la casilla si el donante desea que su nombre aparezca en la web')
    _monto_pyg = models.FloatField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-fecha',)
        verbose_name = 'Donación Recibida'
        verbose_name_plural = 'Donaciones Recibidas'

    def __str__(self):
        return '{} ({})'.format(self.donante, self.fecha)

    def save(self, *args, **kwargs):
        if self.moneda != PYG:
            cambio = self.get_tipo_cambio().cambio
            self._monto_pyg = self.monto * cambio
        else:
            self._monto_pyg = self.monto
        super().save(*args, **kwargs)

    def get_tipo_cambio(self):
        try:
            tipo_cambio = TipoCambio.objects.get(fecha=self.fecha, moneda=self.moneda)
        except TipoCambio.DoesNotExist:
            return None
        return tipo_cambio

    def get_monto_pyg(self):
        return self._monto_pyg

    def clean(self):
        if self.moneda != PYG and not TipoCambio.objects.filter(fecha=self.fecha, moneda=self.moneda).exists():
            raise ValidationError(
                'No se encontró un tipo de cambio para la fecha. Favor ingresar primeramente un tipo de cambio.')


class Concepto(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(
        default='', blank=True, verbose_name='Descripción',
        help_text='Detalles del objeto: Para qué sirve, dónde se usa, etc.')
    medida = models.ForeignKey(
        UnidadMedida, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Unidad de Medida')
    padre = models.ForeignKey(
        'Concepto', null=True, blank=True, on_delete=models.PROTECT, related_name='sub_conceptos', verbose_name='Padre')

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'Concepto'
        verbose_name_plural = 'Conceptos'

    def __str__(self):
        if self.padre:
            return '{}: {} ({})'.format(self.padre.nombre, self.nombre, self.medida)
        return '{} ({})'.format(self.nombre, self.medida)

    def clean(self):
        try:
            self.padre
        except Concepto.DoesNotExist:
            if not self.medida:
                raise ValidationError('Debe Seleccionar una Unidad de Medida')


# class Beneficiario(models.Model):
#     entidad = models.ForeignKey(Entidad, on_delete=models.PROTECT, related_name='+', verbose_name='Entidad')
#     compra = models.ForeignKey('Compra', on_delete=models.PROTECT, related_name='+', verbose_name='Compra')
#     recibido_por = models.CharField(max_length=254, verbose_name='Recibido por', help_text='Nombre y Cargo')
#
#     class Meta:
#         verbose_name = 'Beneficiario'
#         verbose_name_plural = 'Beneficiarios'
#
#     def __str__(self):
#         return self.entidad


class ItemCompra(models.Model):
    compra = models.ForeignKey('Compra', on_delete=models.PROTECT, related_name='items', verbose_name='Compra')
    concepto = models.ForeignKey('Concepto', on_delete=models.PROTECT, related_name='+', verbose_name='Concepto')
    cantidad = models.FloatField(verbose_name='Cantidad')
    precio_unitario = models.FloatField(verbose_name='Precio Unitario')
    precio_total = models.FloatField(verbose_name='Precio Total')
    _precio_unitario_pyg = models.FloatField(editable=False)
    _precio_total_pyg = models.FloatField()

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return '{}: {}'.format(self.concepto, self.cantidad)

    def save(self, *args, **kwargs):
        if self.compra.moneda != PYG:
            cambio = TipoCambio.objects.get(fecha=self.compra.fecha, moneda=self.compra.moneda).cambio
            self._precio_unitario_pyg = self.precio_unitario * cambio
            self._precio_total_pyg = self.precio_total * cambio
        else:
            self._precio_unitario_pyg = self.precio_unitario
            self._precio_total_pyg = self.precio_total
        super().save(*args, **kwargs)

    def clean(self):
        if self.cantidad * self.precio_unitario != self.precio_total:
            raise ValidationError('El Producto de Cantidad y Precio Unitario no coincide con el Precio Total.')
        if not self.concepto.padre:
            raise ValidationError('Debe seleccionar un Concepto detallado.')


class TipoComprobante(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')

    class Meta:
        verbose_name = 'Tipo de Comprobante'
        verbose_name_plural = 'Tipos de Comprobante'

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    fecha = models.DateField(verbose_name='fecha')
    proveedor = models.ForeignKey(Entidad, on_delete=models.PROTECT, related_name='+',
                                  verbose_name='Proveedor/Oferente')
    tipo_comprobante = models.ForeignKey(TipoComprobante, default=1, on_delete=models.PROTECT,
                                         verbose_name='Tipo de Comprobante')
    nro_timbrado = models.IntegerField(null=True, blank=True, verbose_name='Timbrado Nro.')
    nro_comprobante = models.CharField(max_length=50, verbose_name='Comprobante Nro.')
    nro_orden_pago = models.CharField(max_length=50, verbose_name='Orden de Pago Nro.')
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default=PYG, verbose_name='Moneda')

    class Meta:
        ordering = ('-fecha',)
        verbose_name = 'Adquisición Realizada/Destino'
        verbose_name_plural = 'Adquisiciones Realizadas/Destinos'

    def __str__(self):
        return '{} - {}'.format(self.fecha, self.proveedor)

    def clean(self):
        if self.moneda != PYG and not TipoCambio.objects.filter(fecha=self.fecha, moneda=self.moneda).exists():
            raise ValidationError(
                'No se encontró un tipo de cambio para la fecha. Favor ingresar primeramente un tipo de cambio.')