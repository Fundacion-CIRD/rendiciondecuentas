from django.urls import path

from core.views import HomeView, DonacionesView, DonacionAPIView, CompraAPIView

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('donaciones', DonacionesView.as_view(), name='donaciones'),
    path('donaciones/json', DonacionAPIView.as_view(), name='donaciones-json'),
    path('adquisiciones/json', CompraAPIView.as_view(), name='adquisiciones-json'),
]
