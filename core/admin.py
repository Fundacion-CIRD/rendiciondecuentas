from io import BytesIO

import xlsxwriter
from django.contrib import admin
from django.http import FileResponse
from django.urls import path
from rangefilter.filter import DateRangeFilter

from utils.admin import DocumentoInline
from utils.constants import PYG
from utils.models import TipoCambio
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


class DonacionAdmin(admin.ModelAdmin):
    autocomplete_fields = ('donante', 'cuenta',)
    change_list_template = 'entities/donaciones_change_list.html'
    inlines = (DocumentoInline,)
    list_display = ('id', 'fecha', 'donante', 'monto', 'moneda')
    list_display_links = ('id', 'fecha',)
    list_filter = ('cuenta', 'moneda', 'es_anonimo', ('fecha', DateRangeFilter))
    search_fields = ('donante__nombre', 'cuenta__nro', 'cuenta__entidad__nombre', 'nro_comprobante', 'recibo_nro')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('descargar/', self.descargar_excel),
        ]
        return my_urls + urls

    def descargar_excel(self, request):
        qs = self.get_queryset(request)
        qs = qs.filter(**request.GET.dict())
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet(name='Donaciones')
        cabecera = ('ID', 'Fecha', 'Donante', 'Cuenta', 'Nro. Comprobante', 'Nro. Recibo', 'Monto', 'Moneda', 'Cambio', 'Es anonimo')
        row, col = (0, 0)
        for el in cabecera:
            worksheet.write(row, col, el)
            col += 1
        row = 1
        for donacion in qs:
            if donacion.moneda != PYG:
                cambio = TipoCambio.objects.get(fecha=donacion.fecha, moneda=donacion.moneda).cambio
            else:
                cambio = ''
            worksheet.write(row, 0, donacion.id)
            worksheet.write(row, 1, str(donacion.fecha))
            worksheet.write(row, 2, str(donacion.donante))
            worksheet.write(row, 3, str(donacion.cuenta))
            worksheet.write(row, 4, donacion.nro_comprobante)
            worksheet.write(row, 5, donacion.recibo_nro)
            worksheet.write(row, 6, '%.0f' % donacion.monto)
            worksheet.write(row, 7, donacion.moneda)
            worksheet.write(row, 8, cambio)
            worksheet.write(row, 9, 'Sí' if donacion.es_anonimo else 'No')
            row += 1
        workbook.close()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='donaciones.xlsx')


admin.site.register(Donacion, DonacionAdmin)


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
    change_list_template = 'entities/donaciones_change_list.html'
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

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('descargar/', self.descargar_excel),
        ]
        return my_urls + urls

    def descargar_excel(self, request):
        compras = self.get_queryset(request)
        compras = compras.filter(**request.GET.dict())
        items = ItemCompra.objects.filter(compra__in=compras).order_by('compra')
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet(name='Donaciones')
        cabecera = (
            'ID', 'Fecha', 'Proveedor', 'Tipo de Comprobante', 'Nro. de Comprobante',
            'Nro. de Timbrado', 'Nro. de Cheque', 'Moneda', 'Cambio', 'ID Item',
            'Concepto', 'Cantidad', 'Precio Unitario', 'Precio Total'
        )
        row, col = (0, 0)
        for el in cabecera:
            worksheet.write(row, col, el)
            col += 1
        row = 1
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        for item in items:
            if item.compra.moneda != PYG:
                cambio = TipoCambio.objects.get(fecha=item.compra.fecha, moneda=item.compra.moneda).cambio
            else:
                cambio = ''
            worksheet.write(row, 0, item.compra.id)
            worksheet.write_datetime(row, 1, item.compra.fecha, date_format)
            worksheet.write(row, 2, str(item.compra.proveedor))
            worksheet.write(row, 3, str(item.compra.tipo_comprobante))
            worksheet.write(row, 4, item.compra.nro_comprobante)
            worksheet.write(row, 5, item.compra.nro_timbrado)
            worksheet.write(row, 6, item.compra.nro_cheque)
            worksheet.write(row, 7, item.compra.moneda)
            worksheet.write(row, 8, cambio)
            worksheet.write(row, 9, item.id)
            worksheet.write(row, 10, str(item.concepto))
            worksheet.write(row, 11, item.cantidad)
            worksheet.write_number(row, 12, int('%.0f' % item.precio_unitario))
            worksheet.write_number(row, 13, int('%.0f' % item.precio_total))
            row += 1
        workbook.close()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='adquisiciones.xlsx')


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
