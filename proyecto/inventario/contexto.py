# Deja la configuración del sitio disponible en todas las plantillas
# (logo, nombre de la empresa, datos del pie de página, etc.)

from .models import obtener_configuracion

def configuracion_sitio(request):
    return {"configuracion": obtener_configuracion()}
