import re

import pytest
from django.core.exceptions import ValidationError

from utils.models import (
    Documento,
    Foto,
    Galeria,
    TipoCambio,
    UnidadMedida,
    get_upload_path,
)


def test_tipo_cambio_str_returns_correct_string():
    tipo_cambio = TipoCambio(fecha="2020-01-01", cambio="6500")
    assert str(tipo_cambio) == "2020-01-01 6500"


def test_documento_str_returns_complete_string_for_short_descriptions():
    test_description = "test description"
    documento = Documento(
        descripcion=test_description,
    )
    assert str(documento) == "test description"


def test_documento_str_returns_ellipsis_string_for_long_description():
    test_description = "test description that is longer than the short description"
    documento = Documento(
        descripcion=test_description,
    )
    doc_str = str(documento)
    assert len(doc_str) == 20
    assert doc_str[-3:] == "..."


def test_unidad_medida_str_returns_correct_string():
    unidad_medida = UnidadMedida(nombre="Kilogramos")
    assert str(unidad_medida) == "Kilogramos"


@pytest.mark.django_db
def test_unidad_medida_clean_method_raises_error_when_elemental_units_missing_data():
    unidad_elemental = UnidadMedida.objects.create(
        nombre="Kilogramos", acepta_decimales=True
    )
    unidad_medida = UnidadMedida(unidad_elemental=unidad_elemental)
    with pytest.raises(ValidationError) as exception_info:
        unidad_medida.clean()
    assert "Debe cargar la cantidad correspondiente" in str(exception_info.value)
    unidad_medida = UnidadMedida(cant_unidad_elemental=5)
    with pytest.raises(ValidationError) as exception_info:
        unidad_medida.clean()
    assert "Debe seleccionar una unidad" in str(exception_info.value)


@pytest.mark.django_db
def test_upload_path_is_generated_correctly():
    file_regex = r"test-gallery-1/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}.jpg"
    gallery = Galeria.objects.create(nombre="Test Gallery")
    photo = Foto(galeria=gallery)
    filepath = get_upload_path(photo, "sample.jpg")
    assert re.match(file_regex, filepath)


def test_foto_str_returns_correct_string():
    description = "test description"
    foto = Foto(descripcion=description)
    assert str(foto) == description


def test_galeria_str_returns_correct_string():
    name = "Test gallery"
    gallery = Galeria(nombre=name)
    assert str(gallery) == name
