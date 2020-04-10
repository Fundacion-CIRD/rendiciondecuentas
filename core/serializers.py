from rest_framework import serializers

from core.models import Donacion, ItemCompra, Compra
from utils.models import TipoCambio


class DonacionSerializer(serializers.ModelSerializer):
    donante = serializers.SerializerMethodField()
    cuenta = serializers.SerializerMethodField()
    monto = serializers.SerializerMethodField()

    class Meta:
        model = Donacion
        fields = ('id', 'fecha', 'donante', 'cuenta', 'nro_comprobante', 'recibo_nro', 'monto')

    def get_donante(self, obj):
        if obj.es_anonimo:
            return 'Informacion obrante en el CIRD'
        return obj.donante.nombre

    def get_cuenta(self, obj):
        return str(obj.cuenta)

    def get_monto(self, obj):
        return obj.get_monto_pyg()


class ItemCompraSerializer(serializers.ModelSerializer):
    concepto = serializers.SerializerMethodField()
    precio_unitario = serializers.SerializerMethodField()
    precio_total = serializers.SerializerMethodField()

    class Meta:
        model = ItemCompra
        fields = ('concepto', 'cantidad', 'precio_unitario', 'precio_total')

    def get_concepto(self, obj):
        return str(obj.concepto)

    def get_precio_unitario(self, obj):
        if obj.compra.moneda == 'PYG':
            return obj.precio_unitario
        cambio = TipoCambio.objects.get(fecha=obj.compra.fecha, moneda='USD')
        return obj.precio_unitario * cambio

    def get_precio_total(self, obj):
        if obj.compra.moneda == 'PYG':
            return obj.precio_total
        cambio = TipoCambio.objects.get(fecha=obj.compra.fecha, moneda='USD')
        return obj.precio_total * cambio


class CompraSerializer(serializers.ModelSerializer):
    proveedor = serializers.SerializerMethodField()
    tipo_comprobante = serializers.SerializerMethodField()
    items = ItemCompraSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = (
            'id', 'fecha', 'proveedor', 'tipo_comprobante', 'nro_timbrado', 'nro_comprobante', 'nro_cheque',
            'items')

    def get_proveedor(self, obj):
        return str(obj.proveedor)

    def get_tipo_comprobante(self, obj):
        return str(obj.tipo_comprobante)
