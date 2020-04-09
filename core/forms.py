from django import forms


class FiltrosForm(forms.Form):
    fecha_desde = forms.DateField(input_formats=['%d/%m/%Y'], required=False)
    fecha_hasta = forms.DateField(input_formats=['%d/%m/%Y'], required=False)
    monto_desde = forms.FloatField(required=False)
    monto_hasta = forms.FloatField(required=False)


class DonacionesForm(FiltrosForm):
    donante = forms.CharField(required=False)


class AdquisicionesForm(FiltrosForm):
    proveedor = forms.CharField(required=False)
