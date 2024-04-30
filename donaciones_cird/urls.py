from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include(("core.urls", "core"), namespace="core")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
