# Vista para obtener el token de la API (login de apps externas como Flutter).
#
# POST /api/api-token-auth/  con  {"username": "...", "password": "..."}
# Responde {"token": "...", "expira": "...", "dias_duracion": 30}
#
# Está en un archivo aparte de authentication.py para evitar un import
# circular con rest_framework.

from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from .authentication import fecha_vencimiento, token_vencido


class ObtenerTokenView(ObtainAuthToken):
    # Igual que la vista de DRF, pero si el token guardado ya venció lo
    # reemplaza por uno nuevo (si no, la app recibiría un token muerto).
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        token, creado = Token.objects.get_or_create(user=user)
        if not creado and token_vencido(token):
            token.delete()
            token = Token.objects.create(user=user)

        return Response({
            "token": token.key,
            "expira": fecha_vencimiento(token),
            "dias_duracion": getattr(settings, "API_TOKEN_DIAS", 30),
        })
