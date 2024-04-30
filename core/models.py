from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.constants import MONEDA_CHOICES, PYG
from utils.models import TipoCambio, UnidadMedida


class Entidad(models.Model):
    INDIVIDUO = 1
    EMPRESA = 2
    TIPO_ENTIDAD_CHOICES = ((INDIVIDUO, "Individuo"), (EMPRESA, "Empresa"))
    nombre = models.CharField(max_length=254, db_index=True, verbose_name="nombre")
    ruc = models.CharField(max_length=20, default="", blank=True, verbose_name="RUC")
    tipo_entidad = models.PositiveSmallIntegerField(
        choices=TIPO_ENTIDAD_CHOICES, default=INDIVIDUO, verbose_name="Tipo"
    )
    info_extra = models.TextField(
        default="", blank=True, verbose_name="Información Adicional"
    )

    class Meta:
        ordering = ("nombre",)
        verbose_name = "Entidad"
        verbose_name_plural = "Entidades"

    def __str__(self):
        return self.nombre


class TipoCuenta(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")

    class Meta:
        verbose_name = "Tipo de Cuenta"
        verbose_name_plural = "Tipos de Cuenta"

    def __str__(self):
        return self.nombre


class Cuenta(models.Model):
    entidad = models.ForeignKey(
        Entidad, on_delete=models.PROTECT, related_name="+", verbose_name="Entidad"
    )
    tipo = models.ForeignKey(
        TipoCuenta,
        on_delete=models.PROTECT,
        related_name="cuentas",
        verbose_name="Tipo de Cuenta",
    )
    moneda = models.CharField(
        max_length=3, choices=MONEDA_CHOICES, default=PYG, verbose_name="Moneda"
    )
    nro = models.CharField(max_length=50, verbose_name="Cuenta Nro.")

    class Meta:
        ordering = ("entidad",)
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"

    def __str__(self):
        return "{}: {} {} {}".format(
            self.entidad.nombre, self.tipo.nombre, self.get_moneda_display(), self.nro
        )


class Donacion(models.Model):
    fecha = models.DateField(verbose_name="fecha")
    donante = models.ForeignKey(
        Entidad, on_delete=models.PROTECT, related_name="+", verbose_name="nombre"
    )
    cuenta = models.ForeignKey(
        Cuenta, on_delete=models.PROTECT, related_name="ingresos", verbose_name="cuenta"
    )
    nro_comprobante = models.CharField(
        max_length=50, default="", blank=True, verbose_name="Comprobante Nro."
    )
    recibo_nro = models.IntegerField(
        null=True, blank=True, verbose_name="Recibo de Donación Nro."
    )
    monto = models.FloatField(verbose_name="Monto")
    moneda = models.CharField(
        max_length=3, choices=MONEDA_CHOICES, default=PYG, verbose_name="Moneda"
    )
    es_anonimo = models.BooleanField(
        default=True,
        verbose_name="Donante Anonimo",
        help_text=(
            "Desmarcar la casilla si el donante desea que su nombre aparezca en la web"
        ),
    )
    monto_pyg = models.FloatField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-fecha",)
        verbose_name = "Donación Recibida"
        verbose_name_plural = "Donaciones Recibidas"

    def __str__(self):
        return "{} ({})".format(self.donante, self.fecha)

    def save(self, *args, **kwargs):
        if self.moneda != PYG:
            cambio = self.get_tipo_cambio().cambio
            self.monto_pyg = self.monto * cambio
        else:
            self.monto_pyg = self.monto
        super().save(*args, **kwargs)

    def get_tipo_cambio(self):
        try:
            tipo_cambio = TipoCambio.objects.get(fecha=self.fecha, moneda=self.moneda)
        except TipoCambio.DoesNotExist:
            return None
        return tipo_cambio

    def get_monto_pyg(self):
        return self.monto_pyg

    def clean(self):
        if (
            self.moneda != PYG
            and not TipoCambio.objects.filter(
                fecha=self.fecha, moneda=self.moneda
            ).exists()
        ):
            raise ValidationError(
                "No se encontró un tipo de cambio para la fecha. Favor ingresar"
                " primeramente un tipo de cambio."
            )


class Concepto(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(
        default="",
        blank=True,
        verbose_name="Descripción",
        help_text="Detalles del objeto: Para qué sirve, dónde se usa, etc.",
    )
    medida = models.ForeignKey(
        UnidadMedida,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Unidad de Medida",
    )
    padre = models.ForeignKey(
        "Concepto",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="sub_conceptos",
        verbose_name="Padre",
    )

    class Meta:
        ordering = ("nombre",)
        verbose_name = "Concepto"
        verbose_name_plural = "Conceptos"

    def __str__(self):
        if self.padre:
            return "{}: {} ({})".format(self.padre.nombre, self.nombre, self.medida)
        return "{} ({})".format(self.nombre, self.medida)

    def clean(self):
        if self.padre is None and not self.medida:
            raise ValidationError("Debe Seleccionar una Unidad de Medida")


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
    compra = models.ForeignKey(
        "Compra", on_delete=models.PROTECT, related_name="items", verbose_name="Compra"
    )
    concepto = models.ForeignKey(
        "Concepto", on_delete=models.PROTECT, related_name="+", verbose_name="Concepto"
    )
    cantidad = models.FloatField(verbose_name="Cantidad")
    precio_unitario = models.FloatField(verbose_name="Precio Unitario")
    precio_total = models.FloatField(verbose_name="Precio Total")
    precio_unitario_pyg = models.FloatField(editable=False)
    precio_total_pyg = models.FloatField(editable=False)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

    def __str__(self):
        return "{}: {}".format(self.concepto, self.cantidad)

    def save(self, *args, **kwargs):
        if self.compra.moneda != PYG:
            cambio = TipoCambio.objects.get(
                fecha=self.compra.fecha, moneda=self.compra.moneda
            ).cambio
            self.precio_unitario_pyg = self.precio_unitario * cambio
            self.precio_total_pyg = self.precio_total * cambio
        else:
            self.precio_unitario_pyg = self.precio_unitario
            self.precio_total_pyg = self.precio_total
        super().save(*args, **kwargs)

    def clean(self):
        if self.cantidad * self.precio_unitario != self.precio_total:
            raise ValidationError(
                "El Producto de Cantidad y Precio Unitario no coincide con el Precio"
                " Total."
            )

    def get_precio_unitario(self):
        return self.precio_unitario_pyg

    def get_precio_total(self):
        return self.precio_total_pyg


class TipoComprobante(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")

    class Meta:
        verbose_name = "Tipo de Comprobante"
        verbose_name_plural = "Tipos de Comprobante"

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    fecha = models.DateField(verbose_name="fecha")
    proveedor = models.ForeignKey(
        Entidad,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="Proveedor/Oferente",
    )
    tipo_comprobante = models.ForeignKey(
        TipoComprobante,
        default=1,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Comprobante",
    )
    nro_timbrado = models.IntegerField(
        null=True, blank=True, verbose_name="Timbrado Nro."
    )
    nro_comprobante = models.CharField(max_length=50, verbose_name="Comprobante Nro.")
    nro_cheque = models.CharField(max_length=50, verbose_name="Cheque Nro.")
    moneda = models.CharField(
        max_length=3, choices=MONEDA_CHOICES, default=PYG, verbose_name="Moneda"
    )

    class Meta:
        ordering = ("-fecha",)
        verbose_name = "Adquisición Realizada"
        verbose_name_plural = "Adquisiciones Realizadas"

    def __str__(self):
        return "{} - {}".format(self.fecha, self.proveedor)

    def clean(self):
        if (
            self.moneda != PYG
            and not TipoCambio.objects.filter(
                fecha=self.fecha, moneda=self.moneda
            ).exists()
        ):
            raise ValidationError(
                "No se encontró un tipo de cambio para la fecha. Favor ingresar"
                " primeramente un tipo de cambio."
            )

    def get_total_pyg(self):
        suma = 0
        for item in self.items.all():
            suma += item.precio_total_pyg
        return suma


class Entrega(models.Model):
    fecha = models.DateField(verbose_name="Fecha")
    entidad = models.ForeignKey(
        Entidad,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="Entidad Beneficiada",
    )

    class Meta:
        verbose_name = "Entrega"
        verbose_name_plural = "Entregas"

    def __str__(self):
        return "{}({})".format(self.entidad.nombre, self.fecha)


class ItemEntrega(models.Model):
    entrega = models.ForeignKey(
        Entrega,
        on_delete=models.CASCADE,
        related_name="items_entregados",
        verbose_name="Entrega",
    )
    concepto = models.ForeignKey(
        Concepto, on_delete=models.PROTECT, related_name="+", verbose_name="Concepto"
    )
    cantidad = models.FloatField(verbose_name="Cantidad")
    recibido_por = models.CharField(max_length=250, verbose_name="Recibido por")

    class Meta:
        verbose_name = "Item Entregado"
        verbose_name_plural = "Items Entregados"

    def __str__(self):
        return "{}: {}".format(self.concepto, self.cantidad)


@receiver(post_save, sender=TipoCambio)
def update_cambios(sender, instance, created, **kwargs):
    if not created:
        donaciones = Donacion.objects.filter(
            moneda=instance.moneda, fecha=instance.fecha
        )
        updated_donaciones = []
        for d in donaciones:
            d.monto_pyg = d.monto * instance.cambio
            updated_donaciones.append(d)
        Donacion.objects.bulk_update(updated_donaciones, ["monto_pyg"])
        compras = Compra.objects.filter(moneda=instance.moneda, fecha=instance.fecha)
        updated_items = []
        for c in compras:
            for i in c.items.all():
                i.precio_unitario_pyg = i.precio_unitario * instance.cambio
                i.precio_total_pyg = i.precio_total * instance.cambio
                updated_items.append(i)
        ItemCompra.objects.bulk_update(
            updated_items, ["precio_unitario_pyg", "precio_total_pyg"]
        )
