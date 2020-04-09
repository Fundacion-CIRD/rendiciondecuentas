from django.core.paginator import Paginator
from django.db.models import Sum, F, OuterRef, Subquery
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from rest_framework.generics import ListAPIView

from core.forms import DonacionesForm, AdquisicionesForm
from core.models import Donacion, Compra
from core.serializers import DonacionSerializer, CompraSerializer
from utils.constants import PYG, USD
from utils.models import TipoCambio


def filter_query(form, qs, internal_filters):
    filter_query = {}
    for key in form.cleaned_data:
        if form.cleaned_data[key]:
            filter_query[internal_filters[key]] = form.cleaned_data[key]
    qs = qs.filter(**filter_query).distinct()
    return qs


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_donaciones'] = Donacion.objects.aggregate(total=Sum('monto_pyg'))['total']
        adquisiciones = Compra.objects.annotate(total_compra=Sum('items__precio_total_pyg'))
        context['total_adquisiciones'] = adquisiciones.aggregate(total=Sum('total_compra'))['total']
        return context


class DonacionesView(ListView):
    template_name = 'core/donaciones.html'
    model = Donacion
    paginate_by = 10
    filterset_fields = ('donante', 'fecha_desde', 'fecha_hasta', 'monto_desde', 'monto_hasta')
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
        if context.get('is_paginated'):
            context['donaciones'] = context['page_obj']
        else:
            context['donaciones'] = context['donacion_list']
        context['orden'] = self.request.GET.get('orden')
        return context


class AdquisicionesView(ListView):
    template_name = 'core/adquisiciones.html'
    model = Compra
    paginate_by = 10
    filterset_fields = ('proveedor', 'fecha_desde', 'fecha_hasta', 'monto_desde', 'monto_hasta')
    internal_filters = {
        'proveedor': 'proveedor__nombre__icontains',
        'fecha_desde': 'fecha__gte',
        'fecha_hasta': 'fecha__lte',
        'monto_desde': 'monto_pyg__gte',
        'monto_hasta': 'monto_pyg__lte',
    }
    order_fields = ('fecha', '-fecha', 'proveedor', '-proveedor', 'monto', '-monto')
    internal_orders = {
        'fecha': 'fecha',
        '-fecha': '-fecha',
        'proveedor': 'proveedor__nombre',
        '-proveedor': '-proveedor__nombre',
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
        qs = qs.annotate(monto_pyg=Sum('items__precio_total_pyg'))
        form = AdquisicionesForm(data=self.request.GET)
        if form.is_valid():
            qs = filter_query(form, qs, self.internal_filters)
            return qs
        return self.model.objects.none()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['adquisiciones'] = context['page_obj'] if context.get('is_paginated') else context['compra_list']
        context['orden'] = self.request.GET.get('orden')
        return context


class DonacionAPIView(ListAPIView):
    serializer_class = DonacionSerializer
    model = Donacion
    queryset = Donacion.objects.all()


class CompraAPIView(ListAPIView):
    serializer_class = CompraSerializer
    queryset = Compra.objects.all()
