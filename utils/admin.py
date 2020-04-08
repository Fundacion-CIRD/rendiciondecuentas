from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from utils.forms import TipoCambioForm
from utils.models import Documento, UnidadMedida, TipoCambio, Foto, Galeria


class DocumentoInline(GenericTabularInline):
    model = Documento
    extra = 0
    min_num = 0


class TipoCambioAdmin(admin.ModelAdmin):
    form = TipoCambioForm
    list_display = ('fecha', 'cambio', 'moneda')
    list_display_links = ('fecha',)
    list_filter = ('moneda',)


class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviacion', 'unidad_elemental', 'acepta_decimales')
    list_filter = ('unidad_elemental', 'acepta_decimales')
    search_fields = ('nombre', 'abreviacion',)

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['unidad_elemental'].queryset = UnidadMedida.objects.filter(
            unidad_elemental__isnull=True)
        return super().render_change_form(request, context, *args, **kwargs)


class FotoInline(admin.TabularInline):
    model = Foto
    extra = 0
    min_num = 1


class GaleriaAdmin(admin.ModelAdmin):
    inlines = [FotoInline]


admin.site.register(TipoCambio, TipoCambioAdmin)
admin.site.register(UnidadMedida, UnidadMedidaAdmin)
admin.site.register(Galeria, GaleriaAdmin)
