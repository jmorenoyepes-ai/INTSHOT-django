# Envío de correos electrónicos del sistema (bienvenida, pedidos y recuperación).
# Si el servidor de correo falla, el error se registra en la consola pero
# nunca interrumpe el registro de usuarios ni la creación de pedidos.

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from .models import DetallePedido, TokenRecuperacion

logger = logging.getLogger(__name__)


def _direccion_respuesta():
    # Dirección a la que responderá el cliente si le da "Responder"
    return settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL


def _enviar(destinatario, asunto, template, contexto):
    html = render_to_string(template, contexto)
    texto = strip_tags(html)

    correo = EmailMultiAlternatives(
        asunto,
        texto,
        settings.DEFAULT_FROM_EMAIL,
        [destinatario],
    )
    correo.attach_alternative(html, "text/html")
    # Reply-To ayuda a que Gmail no marque el correo como masivo/de una sola vía
    correo.extra_headers["Reply-To"] = _direccion_respuesta()

    try:
        correo.send(fail_silently=False)
    except Exception as error:
        logger.warning("No se pudo enviar el correo '%s' a %s: %s", asunto, destinatario, error)


def _url_publica(request, url):
    # Devuelve la URL completa solo si el sitio está en un dominio real.
    # Los enlaces a localhost/127.0.0.1 hacen que Gmail marque el correo
    # como sospechoso, por eso en desarrollo no se incluyen.
    if request is None:
        return None

    host = request.get_host().split(":")[0]
    if host in ("localhost", "127.0.0.1", "0.0.0.0"):
        return None

    return request.build_absolute_uri(url)


def enviar_bienvenida(usuario, request=None):
    url_login = _url_publica(request, reverse("inventario:login"))

    _enviar(
        usuario.correo,
        f"Bienvenido a INTSHOT, {usuario.nombre}",
        "emails/bienvenida.html",
        {"usuario": usuario, "url_login": url_login},
    )


def enviar_pedido_confirmado(pedido):
    detalles = DetallePedido.objects.filter(pedido=pedido)

    _enviar(
        pedido.usuario.correo,
        f"Pedido #{pedido.id} confirmado - INTSHOT",
        "emails/pedido_confirmado.html",
        {"pedido": pedido, "detalles": detalles},
    )


def enviar_recuperacion(usuario, request):
    # Los tokens anteriores dejan de servir, solo el más reciente es válido
    TokenRecuperacion.objects.filter(usuario=usuario, usado=False).update(usado=True)
    token = TokenRecuperacion.objects.create(usuario=usuario)
    url = request.build_absolute_uri(
        reverse("inventario:restablecer_password", args=[token.token])
    )

    _enviar(
        usuario.correo,
        "Recupera tu contraseña - INTSHOT",
        "emails/recuperar_password.html",
        {"usuario": usuario, "url": url},
    )
