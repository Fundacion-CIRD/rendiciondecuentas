from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include(('core.urls', 'core'), namespace='core')),
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),

]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
