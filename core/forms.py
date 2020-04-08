from django import forms


class DonacionesForm(forms.Form):
    donante = forms.CharField(required=False)
    fecha_desde = forms.DateField(input_formats=['%d/%m/%Y'], required=False)
    fecha_hasta = forms.DateField(input_formats=['%d/%m/%Y'], required=False)
    monto_desde = forms.FloatField(required=False)
    monto_hasta = forms.FloatField(required=False)
