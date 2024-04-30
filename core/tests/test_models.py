import pytest
from django.core.exceptions import ValidationError

from core.models import (
    Compra,
    Concepto,
    Cuenta,
    Donacion,
    Entidad,
    ItemCompra,
    TipoComprobante,
    TipoCuenta,
)
from utils.constants import USD
from utils.models import TipoCambio, UnidadMedida


@pytest.fixture
def entidad():
    return Entidad.objects.create(
        nombre="TestBank",
        tipo_entidad=Entidad.EMPRESA,
    )


@pytest.fixture
def donacion(entidad):
    donor = Entidad.objects.create(
        nombre="TestDonor",
        ruc="1234567-0",
    )
    tipo_cuenta = TipoCuenta.objects.create(nombre="Cuenta Corriente")
    account = Cuenta.objects.create(entidad=entidad, tipo=tipo_cuenta, nro="1234567890")

    return Donacion.objects.create(
        fecha="2020-01-01",
        donante=donor,
        cuenta=account,
        nro_comprobante="123456",
        recibo_nro="123456789",
        monto=12345.65,
    )


@pytest.fixture
def tipo_cambio():
    return TipoCambio.objects.create(fecha="2020-01-01", moneda=USD, cambio=1000)


@pytest.mark.django_db
def test_donacion_save_method_stores_monto_pyg_when_donacion_in_pyg(donacion):
    assert donacion.monto == donacion.monto_pyg


@pytest.mark.django_db
def test_donacion_save_method_converts_currency_when_not_pyg(donacion, tipo_cambio):
    donacion.moneda = USD
    donacion.monto = 5
    tipo_cambio.fecha = donacion.fecha
    tipo_cambio.save()
    donacion.save()
    assert donacion.monto_pyg == 5000


@pytest.mark.django_db
def test_donacion_tipo_cambio_returns_tipo_cambio(donacion, tipo_cambio):
    donacion.moneda = USD
    donacion.monto = 5
    tipo_cambio.fecha = donacion.fecha
    tipo_cambio.save()
    assert donacion.get_tipo_cambio() == tipo_cambio


@pytest.mark.django_db
def test_donacion_tipo_cambio_method_returns_none_when_no_tipo_cambio_found(donacion):
    assert donacion.get_tipo_cambio() is None


@pytest.mark.django_db
def test_donacion_clean_method_raises_error_when_no_tipo_cambio_found(donacion):
    with pytest.raises(ValidationError) as exc_info:
        donacion.moneda = USD
        donacion.clean()
    assert "No se encontró un tipo de cambio para la fecha" in str(exc_info.value)


@pytest.mark.django_db
def test_concepto_clean_method_raies_error_when_no_parent_and_no_unit():
    concepto = Concepto()
    with pytest.raises(ValidationError) as exc_info:
        concepto.clean()
    assert "Debe Seleccionar una Unidad de Medida" in str(exc_info.value)


@pytest.mark.django_db
def test_item_compra_clean_method_raises_error_when_differing_caculated_total():
    item_compra = ItemCompra(cantidad=2, precio_unitario=1, precio_total=1)
    with pytest.raises(ValidationError) as exc_info:
        item_compra.clean()
    assert "El Producto de Cantidad y Precio" in str(exc_info.value)


@pytest.mark.django_db
def test_item_compra_converts_precio_pyg_on_save(tipo_cambio, entidad):
    tipo_comprobante = TipoComprobante.objects.create(nombre="Factura")
    compra = Compra.objects.create(
        fecha=tipo_cambio.fecha,
        proveedor=entidad,
        nro_cheque="1234565",
        moneda=USD,
        tipo_comprobante=tipo_comprobante,
    )
    concepto = Concepto.objects.create(
        nombre="TestConcepto",
        medida=UnidadMedida.objects.create(nombre="Unidad"),
    )
    item_compra = ItemCompra(
        compra=compra,
        concepto=concepto,
        cantidad=5,
        precio_unitario=5,
        precio_total=25,
    )
    item_compra.save()
    assert (
        item_compra.precio_unitario_pyg
        == item_compra.precio_unitario * tipo_cambio.cambio
    )
    assert item_compra.precio_total_pyg == item_compra.precio_total * tipo_cambio.cambio


@pytest.mark.django_db
def test_item_compra_fills_precio_pyg_on_save(entidad):
    tipo_comprobante = TipoComprobante.objects.create(nombre="Factura")
    compra = Compra.objects.create(
        fecha="2020-01-01",
        proveedor=entidad,
        nro_cheque="1234565",
        tipo_comprobante=tipo_comprobante,
    )
    concepto = Concepto.objects.create(
        nombre="TestConcepto",
        medida=UnidadMedida.objects.create(nombre="Unidad"),
    )
    item_compra = ItemCompra(
        compra=compra,
        concepto=concepto,
        cantidad=5,
        precio_unitario=5,
        precio_total=25,
    )
    item_compra.save()
    assert item_compra.precio_total == item_compra.precio_total_pyg
    assert item_compra.precio_unitario == item_compra.precio_unitario_pyg


@pytest.mark.django_db
def test_compra_get_total_pyg_returns_sum_of_items(tipo_cambio, entidad):
    tipo_comprobante = TipoComprobante.objects.create(nombre="Factura")
    compra = Compra.objects.create(
        fecha=tipo_cambio.fecha,
        proveedor=entidad,
        nro_cheque="1234565",
        moneda=USD,
        tipo_comprobante=tipo_comprobante,
    )
    concepto = Concepto.objects.create(
        nombre="TestConcepto",
        medida=UnidadMedida.objects.create(nombre="Unidad"),
    )
    total = 0
    for i in range(3):
        total += ItemCompra.objects.create(
            compra=compra,
            concepto=concepto,
            cantidad=i,
            precio_unitario=5,
            precio_total=25,
        ).precio_total_pyg
    compra_total_pyg = compra.get_total_pyg()
    assert compra_total_pyg > 0 and compra_total_pyg == total
