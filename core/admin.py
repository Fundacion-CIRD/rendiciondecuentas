from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Entidad, Cuenta, Cambio, Documento, Donacion, Compra


class EntidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    list_display_links = ('nombre',)
    search_fields = ('nombre',)


class CuentaAdmin(admin.ModelAdmin):
    list_display = ('entidad', 'tipo')
    list_display_links = ('entidad',)
    list_filter = ('tipo',)
    search_fields = ('entidad__nombre', 'tipo', 'nro')


class CambioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'moneda', 'cambio')
    list_display_links = ('fecha',)
    list_filter = ('cambio',)


class DocumentoInline(GenericTabularInline):
    model = Documento
    extra = 0
    min_num = 0


class DonacionAdmin(admin.ModelAdmin):
    autocomplete_fields = ('origen', 'cuenta',)
    inlines = [DocumentoInline]
    list_display = ('id', 'fecha', 'origen', 'monto_pyg', 'monto_usd')
    list_display_links = ('id', 'fecha',)
    list_filter = ('cuenta',)
    search_fields = ('origen__nombre', 'cuenta__nro', 'cuenta__entidad__nombre', 'nro_comprobante', 'recibo_nro')


class CompraAdmin(admin.ModelAdmin):
    autocomplete_fields = ('proveedor', 'beneficiario')
    inlines = [DocumentoInline]
    list_display = ('id', 'fecha', 'proveedor', 'precio_total_pyg', 'precio_total_usd', 'beneficiario')
    list_display_links = ('fecha',)
    list_filter = ('proveedor', 'beneficiario')
    search_fields = ('proveedor__nombre', 'beneficiario__nombre', 'nro_comprobante', 'concepto')


admin.site.register(Entidad, EntidadAdmin)
admin.site.register(Cuenta, CuentaAdmin)
admin.site.register(Cambio, CambioAdmin)
admin.site.register(Donacion, DonacionAdmin)
admin.site.register(Compra, CompraAdmin)
