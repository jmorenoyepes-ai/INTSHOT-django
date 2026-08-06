from datetime import timedelta
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        print("\n--- 1. ENTRÓ A LA CLASE DE AUTENTICACIÓN ---")
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            print("--- X. EL TOKEN NO EXISTE EN LA BASE DE DATOS ---")
            raise AuthenticationFailed({'error': 'Token inválido', 'is_authenticated': False})

        if not token.user.is_active:
            raise AuthenticationFailed({'error': 'Usuario inactivo', 'is_authenticated': False})

        # Ver tiempo transcurrido
        time_elapsed = timezone.now() - token.created
        print(f"--- 2. TIEMPO TRANSCURRIDO: {time_elapsed} ---")
        print(f"--- 3. ¿Es mayor a 2 minutos?: {time_elapsed > timedelta(hours=24)} ---")

        if time_elapsed > timedelta(minutes=2):
            print("--- 4. EL TOKEN EXPIRÓ. ELIMINANDO DE LA BD... ---")
            token.delete()
            raise AuthenticationFailed({'error': 'El Token ha expirado', 'is_authenticated': False})

        print("--- 5. TOKEN AÚN VÁLIDO ---")
        return (token.user, token)