from django.contrib import admin

from utils.admin import DocumentoInline
from .models import Entidad, Cuenta, Donacion, Compra, Concepto, TipoCuenta, ItemCompra, TipoComprobante


class EntidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    list_display_links = ('nombre',)
    search_fields = ('nombre',)


class CuentaAdmin(admin.ModelAdmin):
    list_display = ('entidad', 'tipo', 'moneda')
    list_display_links = ('entidad',)
    list_filter = ('tipo', 'moneda')
    search_fields = ('entidad__nombre', 'tipo__nombre', 'nro')


class DonacionAdmin(admin.ModelAdmin):
    autocomplete_fields = ('donante', 'cuenta',)
    inlines = (DocumentoInline,)
    list_display = ('id', 'fecha', 'donante', 'monto', 'moneda')
    list_display_links = ('id', 'fecha',)
    list_filter = ('cuenta', 'moneda', 'es_anonimo')
    search_fields = ('donante__nombre', 'cuenta__nro', 'cuenta__entidad__nombre', 'nro_comprobante', 'recibo_nro')


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


class TipoComprobanteAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)


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


admin.site.register(Entidad, EntidadAdmin)
admin.site.register(TipoComprobante, TipoComprobanteAdmin)
admin.site.register(TipoCuenta)
admin.site.register(Cuenta, CuentaAdmin)
admin.site.register(Concepto, ConceptoAdmin)
admin.site.register(Donacion, DonacionAdmin)
admin.site.register(Compra, CompraAdmin)
