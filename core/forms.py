from django import forms


class DonacionesForm(forms.Form):
    donante = forms.CharField(required=False)
    fecha_desde = forms.DateField(input_formats=['%d/%m/%Y'], required=False)
    fecha_hasta = forms.DateField(input_formats=['%d/%m/%Y'], required=False)
    monto_desde = forms.FloatField(required=False)
    monto_hasta = forms.FloatField(required=False)


class AdquisicionesForm(forms.Form):
    concepto = forms.CharField(required=False)
    fecha_desde = forms.DateField(input_formats=['%d/%m/%Y'], required=False)
    fecha_hasta = forms.DateField(input_formats=['%d/%m/%Y'], required=False)
    precio_unitario_desde = forms.FloatField(required=False)
    precio_unitario_hasta = forms.FloatField(required=False)
    precio_total_desde = forms.FloatField(required=False)
    precio_total_hasta = forms.FloatField(required=False)
