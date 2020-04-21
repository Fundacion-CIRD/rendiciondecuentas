from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from utils.admin import DocumentoInline
from .models import Entidad, Cuenta, Donacion, Compra, Concepto, TipoCuenta, ItemCompra, TipoComprobante, ItemEntrega, \
    Entrega


@admin.register(Entidad)
class EntidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    list_display_links = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('entidad', 'tipo', 'moneda')
    list_display_links = ('entidad',)
    list_filter = ('tipo', 'moneda')
    search_fields = ('entidad__nombre', 'tipo__nombre', 'nro')


@admin.register(Donacion)
class DonacionAdmin(admin.ModelAdmin):
    autocomplete_fields = ('donante', 'cuenta',)
    inlines = (DocumentoInline,)
    list_display = ('id', 'fecha', 'donante', 'monto', 'moneda')
    list_display_links = ('id', 'fecha',)
    list_filter = ('cuenta', 'moneda', 'es_anonimo', ('fecha', DateRangeFilter))
    search_fields = ('donante__nombre', 'cuenta__nro', 'cuenta__entidad__nombre', 'nro_comprobante', 'recibo_nro')


@admin.register(Concepto)
class ConceptoAdmin(admin.ModelAdmin):
    autocomplete_fields = ('medida',)
    list_display = ('get_nombre', 'medida')
    search_fields = ('nombre', 'medida__nombre')
    list_filter = ('medida',)

    def get_nombre(self, obj):
        if obj.padre:
            return '{}: {}'.format(obj.padre.nombre, obj.nombre)
        return obj.nombre
    get_nombre.short_description = 'Nombre'


class ItemCompraInline(admin.TabularInline):
    model = ItemCompra
    autocomplete_fields = ('concepto',)
    extra = 0
    min_num = 1


@admin.register(TipoComprobante)
class TipoComprobanteAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    autocomplete_fields = ('proveedor', 'tipo_comprobante')
    inlines = [ItemCompraInline, DocumentoInline]
    list_display = ('id', 'fecha', 'proveedor', 'precio_total',)
    list_display_links = ('fecha',)
    list_filter = ('proveedor', 'tipo_comprobante')
    search_fields = ('proveedor__nombre', 'nro_comprobante', 'nro_orden_pago')

    def precio_total(self, obj):
        if obj.items.all().exists():
            suma = 0.0
            for item in obj.items.all():
                suma += item.precio_total
            return suma
        return None
    precio_total.short_description = 'Precio Total'


class ItemEntregaInline(admin.TabularInline):
    model = ItemEntrega
    min_num = 1
    extra = 0


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'entidad')
    list_filter = ('entidad',)
    inlines = [ItemEntregaInline, DocumentoInline]


admin.site.register(TipoCuenta)
