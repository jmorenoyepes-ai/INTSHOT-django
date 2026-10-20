from django.contrib import admin
from django.urls import path, include
from inventario import views
from inventario.token_views import ObtenerTokenView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('inventario.urls')),
    path('api/', include('inventario.urls_api')),
    path('api/auth/', include('rest_framework.urls')),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # Endpoint para generar/obtener tokens
    path('api/api-token-auth/', ObtenerTokenView.as_view(), name='api_token_auth'),

]

# Imágenes subidas por los usuarios (productos, logo, etc.)
# En desarrollo las sirve el helper static(). En producción lo ideal es que
# las sirva el servidor web (en PythonAnywhere: pestaña Web > Static files,
# URL /media/ -> carpeta media/). Si no está configurado, esta ruta las sirve
# igual para que el sitio no quede sin imágenes.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]

# Páginas de error personalizadas (se usan cuando DEBUG = False)
handler404 = "inventario.views.pagina_404"
handler500 = "inventario.views.pagina_500"