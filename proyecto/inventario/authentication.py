# Autenticación por token de la API (para apps externas como Flutter).
#
# Un token vence API_TOKEN_DIAS días después de haberse creado (ver settings).
# Cuando vence se borra y la app debe pedir uno nuevo en /api/api-token-auth/,
# que siempre devuelve un token vigente junto con su fecha de vencimiento
# (ver ObtenerTokenView en token_views.py).

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


def duracion_token():
    return timedelta(days=getattr(settings, "API_TOKEN_DIAS", 30))


def token_vencido(token):
    return timezone.now() - token.created > duracion_token()


def fecha_vencimiento(token):
    return token.created + duracion_token()


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed({"error": "Token inválido", "is_authenticated": False})

        if not token.user.is_active:
            raise AuthenticationFailed({"error": "Usuario inactivo", "is_authenticated": False})

        if token_vencido(token):
            token.delete()
            raise AuthenticationFailed({"error": "El Token ha expirado", "is_authenticated": False})

        return (token.user, token)
