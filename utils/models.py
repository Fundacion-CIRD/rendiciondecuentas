import os
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from .constants import MONEDA_CHOICES, USD


class TipoCambio(models.Model):
    fecha = models.DateField(verbose_name='fecha')
    cambio = models.FloatField(verbose_name='cambio')
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default=USD, verbose_name='Moneda')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-fecha',)
        unique_together = ('fecha', 'moneda')
        verbose_name = 'Tipo de Cambio'
        verbose_name_plural = 'Tipos de Cambio'

    def __str__(self):
        return '{} {}'.format(self.fecha, self.cambio)


class Documento(models.Model):
    archivo = models.FileField(upload_to='documentos', verbose_name='Archivo')
    descripcion = models.TextField(default='', blank=True, verbose_name='Descripción')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        if len(self.descripcion) > 20:
            return '{}...'.format(self.descripcion[:17])
        return self.descripcion


class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre', help_text='Escribir en Plural. Ej.: Kilogramos.')
    abreviacion = models.CharField(
        max_length=10, default='', blank=True, verbose_name='Abreviación', help_text='Ej.: Kg. para Kilogramos.')
    unidad_elemental = models.ForeignKey(
        'UnidadMedida', null=True, blank=True, on_delete=models.PROTECT, related_name='+',
        verbose_name='Unidad de Medida Elemental', help_text='Ej. Kg., m.,')
    cant_unidad_elemental = models.FloatField(
        null=True, blank=True, verbose_name='Cantidad en Unidad Elemental',
        help_text='Para una caja de 100 items, escribir 100.')
    acepta_decimales = models.BooleanField(default=False, verbose_name='Acepta valores con coma')

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.unidad_elemental and not self.cant_unidad_elemental:
            raise ValidationError('Debe cargar la cantidad correspondiente en Unidades Elementales')
        if self.cant_unidad_elemental and not self.unidad_elemental:
            raise ValidationError('Debe seleccionar una unidad de medida elemental.')


def get_upload_path(instance, filename):
    galeria_slug = '{}-{}'.format(slugify(instance.galeria.nombre), instance.galeria.id)
    extension = filename.split('.')[-1]
    new_filename = '{}.{}'.format(uuid.uuid4(), extension)
    return os.path.join(galeria_slug, new_filename)


class Foto(models.Model):
    archivo = models.ImageField(upload_to=get_upload_path, verbose_name='Imagen')
    descripcion = models.CharField(max_length=250, verbose_name='Descripción')
    galeria = models.ForeignKey('Galeria', on_delete=models.PROTECT, verbose_name='Galería')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'

    def __str__(self):
        return self.descripcion


class Galeria(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')

    class Meta:
        verbose_name = 'Galería'
        verbose_name_plural = 'Galerías'

    def __str__(self):
        return self.nombre
