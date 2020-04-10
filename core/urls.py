from django.urls import path

from core.views import HomeView, DonacionesView, DonacionAPIView, CompraAPIView, AdquisicionesView, \
    DetalleAdquisicionView, descargar_donaciones, descargar_adquisiciones

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('donaciones', DonacionesView.as_view(), name='donaciones'),
    path('donaciones/json', DonacionAPIView.as_view(), name='donaciones-json'),
    path('donaciones/descargar', descargar_donaciones, name='donaciones-excel'),
    path('adquisiciones', AdquisicionesView.as_view(), name='adquisiciones'),
    path('adquisiciones/descargar', descargar_adquisiciones, name='adquisiciones-excel'),
    path('adquisiciones/json', CompraAPIView.as_view(), name='adquisiciones-json'),
    path('adquisiciones/<pk>', DetalleAdquisicionView.as_view(), name='detalle-adquisiciones'),
]
