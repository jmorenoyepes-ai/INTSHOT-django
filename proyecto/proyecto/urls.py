from django.contrib import admin
from django.urls import path, include
from inventario import views
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static

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
    path('api/api-token-auth/', obtain_auth_token, name='api_token_auth'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)