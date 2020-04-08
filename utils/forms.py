from django import forms

from utils.models import TipoCambio


class TipoCambioForm(forms.ModelForm):
    cambio = forms.FloatField(localize=True)

    class Meta:
        model = TipoCambio
        fields = '__all__'
