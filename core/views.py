from io import BytesIO

import xlsxwriter
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.db.models.functions import ConcatPair
from django.http import FileResponse
from django.views.generic import TemplateView, ListView, DetailView
from rest_framework.generics import ListAPIView

from core.forms import DonacionesForm, AdquisicionesForm
from core.graph_utils import total_por_concepto
from core.models import Donacion, Compra, ItemCompra
from core.serializers import DonacionSerializer, CompraSerializer
from utils.models import Galeria, Documento, Foto


def contains_any(a, b):
    for el in a:
        if el in b:
            return True
    return False


def filter_query(form, qs, internal_filters):
    fq = {}
    for key in form.cleaned_data:
        if form.cleaned_data[key]:
            fq[internal_filters[key]] = form.cleaned_data[key]
    qs = qs.filter(**fq).distinct()
    return qs


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculos para el resumen
        context['total_donaciones'] = Donacion.objects.aggregate(total=Sum('monto_pyg'))['total']
        adquisiciones = Compra.objects.annotate(total_compra=Sum('items__precio_total_pyg'))
        context['total_adquisiciones'] = adquisiciones.aggregate(total=Sum('total_compra'))['total']
        if context['total_donaciones'] and context['total_adquisiciones']:
            context['saldo'] = context['total_donaciones'] - context['total_adquisiciones']

        # ultima fecha de actualizacion
        ultima_donacion = Donacion.objects.order_by('-fecha').first()
        ultima_adquisicion = Compra.objects.order_by('-fecha').first()
        context['ultima_actualizacion'] = \
            ultima_donacion.fecha if ultima_donacion.fecha > ultima_adquisicion.fecha else ultima_adquisicion.fecha

        # Calculos para el grafico
        conceptos = total_por_concepto()
        context['labels'] = [el for el in conceptos.keys()]
        context['data'] = ['%.0f' % el for el in conceptos.values()]
        return context


class AntecedentesView(TemplateView):
    template_name = 'core/antecedentes.html'


class DonacionesView(ListView):
    template_name = 'core/donaciones.html'
    model = Donacion
    paginate_by = 10
    internal_filters = {
        'donante': 'donante__nombre__icontains',
        'fecha_desde': 'fecha__gte',
        'fecha_hasta': 'fecha__lte',
        'monto_desde': 'monto_pyg__gte',
        'monto_hasta': 'monto_pyg__lte',
    }
    order_fields = ('fecha', '-fecha', 'donante', '-donante', 'monto', '-monto')
    internal_orders = {
        'fecha': 'fecha',
        '-fecha': '-fecha',
        'donante': ('-es_anonimo', 'donante__nombre'),
        '-donante': ('-es_anonimo', '-donante__nombre'),
        'monto': 'monto_pyg',
        '-monto': '-monto_pyg',
    }

    def get_ordering(self):
        ordering = self.request.GET.get('orden')
        if ordering in self.order_fields:
            return self.internal_orders[ordering]
        return '-fecha'

    def get_queryset(self):
        qs = super().get_queryset()
        form = DonacionesForm(data=self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('donante'):
                qs = qs.filter(es_anonimo=False)
            qs = filter_query(form, qs, self.internal_filters)
            return qs
        return self.model.objects.none()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        # context['total_donaciones'] = Donacion.objects.aggregate(total=Sum('monto_pyg'))['total']
        context['total_donaciones'] = context['donacion_list'].aggregate(total=Sum('monto_pyg'))['total']
        if contains_any(self.request.GET.keys(), self.internal_filters.keys()):
            context['filtered'] = True
        if context.get('is_paginated'):
            context['donaciones'] = context['page_obj']
        else:
            context['donaciones'] = context['donacion_list']
        context['orden'] = self.request.GET.get('orden')
        return context


def descargar_donaciones(request):
    internal_filters = {
        'donante': 'donante__nombre__icontains',
        'fecha_desde': 'fecha__gte',
        'fecha_hasta': 'fecha__lte',
        'monto_desde': 'monto_pyg__gte',
        'monto_hasta': 'monto_pyg__lte',
    }
    qs = Donacion.objects.all().select_related('donante')
    form = DonacionesForm(data=request.GET)
    if form.is_valid():
        if form.cleaned_data.get('donante'):
            qs = qs.filter(es_anonimo=False)
        qs = filter_query(form, qs, internal_filters)
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet(name='Donaciones')
    cabecera = ('ID', 'Fecha', 'Donante', 'Nro. Comprobante', 'Nro. Recibo', 'Monto')
    row, col = (0, 0)
    for el in cabecera:
        worksheet.write(row, col, el)
        col += 1
    row = 1
    for donacion in qs:
        worksheet.write(row, 0, donacion.id)
        worksheet.write(row, 1, str(donacion.fecha))
        worksheet.write(row, 2, str(donacion.donante) if not donacion.es_anonimo else 'Información Obrante en el CIRD')
        # worksheet.write(row, 3, str(donacion.cuenta))
        worksheet.write(row, 3, donacion.nro_comprobante)
        worksheet.write(row, 4, donacion.recibo_nro)
        worksheet.write(row, 5, '%.0f' % donacion.monto_pyg)
        row += 1
    workbook.close()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='donaciones.xlsx')


class AdquisicionesView(ListView):
    template_name = 'core/adquisiciones.html'
    model = ItemCompra
    paginate_by = 10
    internal_filters = {
        'concepto': 'concept_name__icontains',
        'fecha_desde': 'compra__fecha__gte',
        'fecha_hasta': 'compra__fecha__lte',
        'precio_unitario_desde': 'precio_unitario_pyg__gte',
        'precio_unitario_hasta': 'precio_unitario_pyg__lte',
        'precio_total_desde': 'precio_total_pyg__gte',
        'precio_total_hasta': 'precio_total_pyg__lte',
    }
    order_fields = (
        'fecha', '-fecha', 'concepto', '-concepto', 'precio_unitario', '-precio_unitario', 'precio_total',
        '-precio_total')
    internal_orders = {
        'fecha': 'compra__fecha',
        '-fecha': '-compra__fecha',
        'concepto': 'concept_name',
        '-concepto': '-concept_name',
        'precio_unitario': 'precio_unitario_pyg',
        '-precio_unitario': '-precio_unitario_pyg',
        'precio_total': 'precio_total_pyg',
        '-precio_total': '-precio_total_pyg',
    }

    def get_ordering(self):
        ordering = self.request.GET.get('orden')
        if ordering in self.order_fields:
            return self.internal_orders[ordering]
        return '-compra__fecha'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            concept_name=ConcatPair('concepto__padre__nombre', 'concepto__nombre', 'concepto__medida__nombre'))
        form = AdquisicionesForm(data=self.request.GET)
        if form.is_valid():
            qs = filter_query(form, qs, self.internal_filters)
            return qs
        return self.model.objects.none()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['items'] = context['page_obj'] if context.get('is_paginated') else context['itemcompra_list']
        adquisiciones = Compra.objects.filter(items__in=context['items']).annotate(total_compra=Sum('items__precio_total_pyg'))
        # adquisiciones = Compra.objects.annotate(total_compra=Sum('items__precio_total_pyg'))
        context['total_adquisiciones'] = adquisiciones.aggregate(total=Sum('total_compra'))['total']
        context['orden'] = self.request.GET.get('orden')
        if contains_any(self.request.GET.keys(), self.internal_filters.keys()):
            context['filtered'] = True
        return context


def descargar_adquisiciones(request):
    adquisiciones = Compra.objects.all().prefetch_related('proveedor', 'items', 'tipo_comprobante')
    adquisiciones = adquisiciones.annotate(monto_pyg=Sum('items__precio_total_pyg'))
    items = ItemCompra.objects.filter(compra__in=adquisiciones)
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet('Adquisiciones')
    cabecera_adquisiciones = (
        'ID', 'Fecha', 'Proveedor', 'Tipo de Comprobante', 'Nro. de Comprobante', 'Nro. de Timbrado', 'Nro. de Cheque',
        'Total Adquisición')
    cabecera_items = ('ID', 'ID Adquisición', 'Concepto', 'Cantidad', 'Precio Unitario', 'Precio Total')
    row, col = (0, 0)
    for el in cabecera_adquisiciones:
        worksheet.write(row, col, el)
        col += 1
    row = 1
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    for adquisicion in adquisiciones:
        worksheet.write(row, 0, adquisicion.id)
        worksheet.write_datetime(row, 1, adquisicion.fecha, date_format)
        worksheet.write(row, 2, str(adquisicion.proveedor))
        worksheet.write(row, 3, str(adquisicion.tipo_comprobante))
        worksheet.write(row, 4, adquisicion.nro_comprobante)
        worksheet.write(row, 5, adquisicion.nro_timbrado)
        worksheet.write(row, 6, adquisicion.nro_cheque)
        worksheet.write_number(row, 7, int('%.0f' % adquisicion.monto_pyg))
        row += 1
    worksheet = workbook.add_worksheet('Items Adquiridos')
    row, col = (0, 0)
    for el in cabecera_items:
        worksheet.write(row, col, el)
        col += 1
    row = 1
    for item in items:
        worksheet.write(row, 0, item.id)
        worksheet.write(row, 1, item.compra.id)
        worksheet.write(row, 2, str(item.concepto))
        worksheet.write(row, 3, item.cantidad)
        worksheet.write_number(row, 4, int('%.0f' % item.precio_unitario_pyg))
        worksheet.write_number(row, 5, int('%.0f' % item.precio_total_pyg))
        row += 1
    workbook.close()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='adquisiciones.xlsx')


class DetalleAdquisicionView(DetailView):
    model = Compra
    template_name = 'core/detalle_adquisicion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_adquisicion'] = context['object'].items.aggregate(total=Sum('precio_total_pyg'))['total']
        content_type = ContentType.objects.get_for_model(Compra)
        context['documentos'] = Documento.objects.filter(object_id=context['object'].id, content_type=content_type)
        return context


class DonacionAPIView(ListAPIView):
    serializer_class = DonacionSerializer
    model = Donacion
    queryset = Donacion.objects.all()


class CompraAPIView(ListAPIView):
    serializer_class = CompraSerializer
    queryset = Compra.objects.all()


class GaleriaView(ListView):
    template_name = 'core/gallery.html'
    model = Foto
    paginate_by = 18

    def get_queryset(self):
        try:
            galeria = Galeria.objects.get(pk=1)
            return galeria.foto_set.all()
        except Galeria.DoesNotExist:
            return Foto.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context.get('is_paginated'):
            context['fotos'] = context['page_obj']
        else:
            context['fotos'] = context['foto_list']
        return context
