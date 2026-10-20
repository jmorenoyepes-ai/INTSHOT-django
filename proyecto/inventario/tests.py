# Pruebas automatizadas de INTSHOT.
# Ejecutar con:  python manage.py test inventario
#
# Cubren los flujos principales del sistema (registro, login, roles, carrito,
# pedidos, pagos, compras, recuperación de contraseña y API) y además
# verifican reglas de seguridad: que un cliente no pueda ver ni pagar
# pedidos de otro cliente, ni tocar el carrito de otro, etc.

from datetime import timedelta
from decimal import Decimal

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import (
    Carrito, Compra, DetalleCompra, DetallePedido, MovimientoContable,
    MovimientoInventario, Pago, Pedido, Producto, Proveedor,
    TokenRecuperacion, Usuario,
)
from .utilidades import guardar_password


EMAIL_PRUEBAS = "django.core.mail.backends.locmem.EmailBackend"


def crear_usuario(correo, rol="Cliente", clave="clave12345", nombre="Ana", apellido="Prueba"):
    u = Usuario(nombre=nombre, apellido=apellido, correo=correo, telefono="3001234567", rol=rol)
    guardar_password(u, clave)
    u.save()
    return u


def crear_producto(nombre="Camiseta", stock=10, precio="25000.00", categoria="Camisetas"):
    return Producto.objects.create(
        nombre=nombre, color="Negro", descripcion="Desc", talla="M",
        stock=stock, precio=Decimal(precio), categoria=categoria,
    )


@override_settings(EMAIL_BACKEND=EMAIL_PRUEBAS)
class BaseIntshot(TestCase):
    def setUp(self):
        self.admin = crear_usuario("admin@test.com", "Administrador")
        self.empleado = crear_usuario("empleado@test.com", "Empleado")
        self.cliente = crear_usuario("cliente@test.com", "Cliente")
        self.otro_cliente = crear_usuario("otro@test.com", "Cliente")
        self.producto = crear_producto()

    def login(self, usuario, clave="clave12345"):
        r = self.client.post(reverse("inventario:login"), {"user": usuario.correo, "password": clave})
        self.assertRedirects(r, reverse("inventario:inicio"), fetch_redirect_response=False)
        return r

    def mensajes(self, response):
        return [str(m) for m in response.context["messages"]] if response.context else []


# ---------------------------------------------------------------------------
# Páginas públicas
# ---------------------------------------------------------------------------

class PaginasPublicasTests(BaseIntshot):
    def test_landing_carga(self):
        r = self.client.get(reverse("inventario:landing"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Camiseta")

    def test_catalogo_publico_carga_y_busca(self):
        r = self.client.get(reverse("inventario:catalogo_publico"), {"buscar": "Camiseta"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Camiseta")

    def test_catalogo_publico_oculta_sin_stock(self):
        crear_producto(nombre="Agotado", stock=0)
        r = self.client.get(reverse("inventario:catalogo_publico"))
        self.assertNotContains(r, "Agotado")

    def test_detalle_publico_producto_inexistente_redirige(self):
        r = self.client.get(reverse("inventario:detalle_producto_publico", args=[9999]))
        self.assertRedirects(r, reverse("inventario:catalogo_publico"))

    def test_comprar_sin_login_pide_login(self):
        r = self.client.get(reverse("inventario:comprar_producto", args=[self.producto.id]))
        self.assertRedirects(r, reverse("inventario:login"))


# ---------------------------------------------------------------------------
# Registro y login
# ---------------------------------------------------------------------------

class AutenticacionTests(BaseIntshot):
    def test_registro_crea_usuario_con_password_hasheada_y_envia_correo(self):
        datos = {
            "nombre": "Juan", "apellido": "Perez", "correo": "nuevo@test.com",
            "telefono": "3001112233", "password": "secreta1", "veri_password": "secreta1",
        }
        r = self.client.post(reverse("inventario:registrarse"), datos)
        self.assertRedirects(r, reverse("inventario:login"))
        u = Usuario.objects.get(correo="nuevo@test.com")
        self.assertEqual(u.rol, "Cliente")
        self.assertTrue(u.password.startswith("pbkdf2_"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("nuevo@test.com", mail.outbox[0].to)

    def test_registro_rechaza_correo_duplicado(self):
        datos = {
            "nombre": "Juan", "apellido": "Perez", "correo": self.cliente.correo,
            "telefono": "3001112233", "password": "secreta1", "veri_password": "secreta1",
        }
        r = self.client.post(reverse("inventario:registrarse"), datos)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Usuario.objects.filter(correo=self.cliente.correo).count(), 1)

    def test_registro_rechaza_passwords_distintas(self):
        datos = {
            "nombre": "Juan", "apellido": "Perez", "correo": "x@test.com",
            "telefono": "3001112233", "password": "secreta1", "veri_password": "otra",
        }
        r = self.client.post(reverse("inventario:registrarse"), datos)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Usuario.objects.filter(correo="x@test.com").exists())

    def test_login_correcto_guarda_sesion(self):
        self.login(self.cliente)
        self.assertEqual(self.client.session["logueado"]["rol"], "Cliente")

    def test_login_incorrecto(self):
        r = self.client.post(reverse("inventario:login"), {"user": self.cliente.correo, "password": "mala"})
        self.assertRedirects(r, reverse("inventario:login"))
        self.assertFalse(self.client.session.get("logueado"))

    def test_login_password_texto_plano_se_migra_a_hash(self):
        viejo = Usuario.objects.create(
            nombre="Viejo", apellido="Usuario", correo="viejo@test.com",
            telefono="3000000000", password="plano123", rol="Cliente",
        )
        self.login(viejo, "plano123")
        viejo.refresh_from_db()
        self.assertTrue(viejo.password.startswith("pbkdf2_"))

    def test_logout(self):
        self.login(self.cliente)
        r = self.client.get(reverse("inventario:logout"))
        self.assertRedirects(r, reverse("inventario:login"))
        self.assertNotIn("logueado", self.client.session)

    def test_sin_login_redirige(self):
        r = self.client.get(reverse("inventario:inicio"))
        self.assertRedirects(r, reverse("inventario:login"))

    def test_bloqueo_tras_varios_intentos_fallidos(self):
        from django.core.cache import cache
        cache.clear()
        for _ in range(5):
            self.client.post(reverse("inventario:login"), {"user": self.cliente.correo, "password": "mala"})
        # Aunque ahora la clave sea correcta, el correo está bloqueado
        r = self.client.post(reverse("inventario:login"), {"user": self.cliente.correo, "password": "clave12345"})
        self.assertRedirects(r, reverse("inventario:login"), fetch_redirect_response=False)
        self.assertFalse(self.client.session.get("logueado"))
        cache.clear()

    def test_password_corta_rechazada(self):
        datos = {
            "nombre": "Juan", "apellido": "Perez", "correo": "corta@test.com",
            "telefono": "3001112233", "password": "abc12", "veri_password": "abc12",
        }
        self.client.post(reverse("inventario:registrarse"), datos)
        self.assertFalse(Usuario.objects.filter(correo="corta@test.com").exists())


# ---------------------------------------------------------------------------
# Recuperación de contraseña
# ---------------------------------------------------------------------------

class RecuperacionPasswordTests(BaseIntshot):
    def test_solicitud_envia_correo_con_token(self):
        r = self.client.post(reverse("inventario:solicitar_password"), {"correo": self.cliente.correo})
        self.assertRedirects(r, reverse("inventario:login"))
        self.assertEqual(len(mail.outbox), 1)
        token = TokenRecuperacion.objects.get(usuario=self.cliente)
        self.assertIn(str(token.token), mail.outbox[0].body)

    def test_solicitud_correo_inexistente_no_revela_nada(self):
        r = self.client.post(reverse("inventario:solicitar_password"), {"correo": "nadie@test.com"})
        self.assertRedirects(r, reverse("inventario:login"))
        self.assertEqual(len(mail.outbox), 0)

    def test_restablecer_con_token_valido(self):
        token = TokenRecuperacion.objects.create(usuario=self.cliente)
        url = reverse("inventario:restablecer_password", args=[token.token])
        r = self.client.post(url, {"password": "nueva123", "veri_password": "nueva123"})
        self.assertRedirects(r, reverse("inventario:login"))
        token.refresh_from_db()
        self.assertTrue(token.usado)
        self.login(self.cliente, "nueva123")

    def test_token_usado_no_sirve(self):
        token = TokenRecuperacion.objects.create(usuario=self.cliente, usado=True)
        url = reverse("inventario:restablecer_password", args=[token.token])
        r = self.client.get(url)
        self.assertRedirects(r, reverse("inventario:solicitar_password"))

    def test_token_vencido_no_sirve(self):
        token = TokenRecuperacion.objects.create(usuario=self.cliente)
        TokenRecuperacion.objects.filter(pk=token.pk).update(creado=timezone.now() - timedelta(hours=2))
        url = reverse("inventario:restablecer_password", args=[token.token])
        r = self.client.get(url)
        self.assertRedirects(r, reverse("inventario:solicitar_password"))


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

class RolesTests(BaseIntshot):
    def test_cliente_no_entra_a_modulos_administrativos(self):
        self.login(self.cliente)
        for nombre in ["usuarios", "productos", "proveedores", "compras", "pagos",
                       "movimientos", "contabilidad", "configuracion", "dashboard"]:
            r = self.client.get(reverse(f"inventario:{nombre}"))
            self.assertRedirects(r, reverse("inventario:inicio"), msg_prefix=nombre)

    def test_empleado_no_entra_a_usuarios_ni_contabilidad(self):
        self.login(self.empleado)
        for nombre in ["usuarios", "contabilidad", "configuracion"]:
            r = self.client.get(reverse(f"inventario:{nombre}"))
            self.assertRedirects(r, reverse("inventario:inicio"), msg_prefix=nombre)

    def test_empleado_entra_a_productos_y_dashboard(self):
        self.login(self.empleado)
        for nombre in ["productos", "proveedores", "compras", "pagos", "movimientos", "dashboard"]:
            r = self.client.get(reverse(f"inventario:{nombre}"))
            self.assertEqual(r.status_code, 200, nombre)

    def test_admin_entra_a_todo(self):
        self.login(self.admin)
        for nombre in ["usuarios", "productos", "proveedores", "compras", "pagos",
                       "movimientos", "contabilidad", "configuracion", "dashboard", "pedidos"]:
            r = self.client.get(reverse(f"inventario:{nombre}"))
            self.assertEqual(r.status_code, 200, nombre)

    def test_dashboard_oculta_dinero_a_empleado(self):
        self.login(self.empleado)
        r = self.client.get(reverse("inventario:dashboard"))
        self.assertFalse(r.context["es_administrador"])


# ---------------------------------------------------------------------------
# Usuarios (admin)
# ---------------------------------------------------------------------------

class UsuariosAdminTests(BaseIntshot):
    def test_crear_usuario(self):
        self.login(self.admin)
        datos = {
            "nombre": "Nuevo", "apellido": "Empleado", "correo": "ne@test.com",
            "telefono": "3001112233", "rol": "Empleado",
            "password": "clave123", "veri_password": "clave123",
        }
        r = self.client.post(reverse("inventario:crear_usuario"), datos)
        self.assertRedirects(r, reverse("inventario:usuarios"))
        self.assertTrue(Usuario.objects.filter(correo="ne@test.com", rol="Empleado").exists())

    def test_no_eliminar_administrador(self):
        self.login(self.admin)
        otro_admin = crear_usuario("admin2@test.com", "Administrador")
        self.client.post(reverse("inventario:eliminar_usuario", args=[otro_admin.id]))
        self.assertTrue(Usuario.objects.filter(pk=otro_admin.pk).exists())

    def test_eliminar_cliente_sin_pedidos(self):
        self.login(self.admin)
        self.client.post(reverse("inventario:eliminar_usuario", args=[self.otro_cliente.id]))
        self.assertFalse(Usuario.objects.filter(pk=self.otro_cliente.pk).exists())

    def test_no_eliminar_cliente_con_pedidos(self):
        self.login(self.admin)
        Pedido.objects.create(usuario=self.otro_cliente)
        self.client.post(reverse("inventario:eliminar_usuario", args=[self.otro_cliente.id]))
        self.assertTrue(Usuario.objects.filter(pk=self.otro_cliente.pk).exists())


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

class ProductosTests(BaseIntshot):
    def test_crear_producto(self):
        self.login(self.empleado)
        datos = {
            "nombre": "Jean", "color": "Azul", "descripcion": "Jean clásico",
            "categoria": "Pantalones", "talla": "32", "stock": "5", "precio": "80000",
        }
        r = self.client.post(reverse("inventario:crear_producto"), datos)
        self.assertRedirects(r, reverse("inventario:productos"))
        self.assertTrue(Producto.objects.filter(nombre="Jean").exists())

    def test_crear_producto_rechaza_precio_cero_y_stock_negativo(self):
        self.login(self.empleado)
        datos = {
            "nombre": "Malo", "color": "Azul", "descripcion": "x",
            "categoria": "Pantalones", "talla": "32", "stock": "-1", "precio": "0",
        }
        r = self.client.post(reverse("inventario:crear_producto"), datos)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Producto.objects.filter(nombre="Malo").exists())

    def test_actualizar_producto(self):
        self.login(self.empleado)
        datos = {
            "nombre": "Camiseta Editada", "color": "Negro", "descripcion": "Desc",
            "categoria": "Camisetas", "talla": "M", "stock": "10", "precio": "25000",
        }
        self.client.post(reverse("inventario:actualizar_producto", args=[self.producto.id]), datos)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, "Camiseta Editada")

    def test_no_eliminar_producto_con_pedidos(self):
        self.login(self.empleado)
        pedido = Pedido.objects.create(usuario=self.cliente)
        DetallePedido.objects.create(pedido=pedido, producto=self.producto, cantidad=1, precio_unitario=1)
        self.client.post(reverse("inventario:eliminar_producto", args=[self.producto.id]))
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())


# ---------------------------------------------------------------------------
# Carrito, pedidos y pagos (flujo completo del cliente)
# ---------------------------------------------------------------------------

class FlujoCompraClienteTests(BaseIntshot):
    def _agregar_al_carrito(self, producto=None):
        producto = producto or self.producto
        return self.client.get(reverse("inventario:agregar_carrito", args=[producto.id]))

    def _datos_confirmacion(self):
        # Simula los campos ocultos que envía el carrito al confirmar
        items = Carrito.objects.filter(usuario=self.cliente)
        datos = {
            "item_visto": [str(i.id) for i in items],
            "nombre_visto": [i.producto.nombre for i in items],
            "color_visto": [i.producto.color for i in items],
            "descripcion_vista": [i.producto.descripcion for i in items],
            "talla_vista": [i.producto.talla for i in items],
            "categoria_vista": [i.producto.categoria for i in items],
            "precio_visto": [str(i.producto.precio) for i in items],
        }
        return datos

    def test_agregar_al_carrito_acumula_cantidad(self):
        self.login(self.cliente)
        self._agregar_al_carrito()
        self._agregar_al_carrito()
        item = Carrito.objects.get(usuario=self.cliente, producto=self.producto)
        self.assertEqual(item.cantidad, 2)

    def test_actualizar_carrito_respeta_stock(self):
        self.login(self.cliente)
        self._agregar_al_carrito()
        item = Carrito.objects.get(usuario=self.cliente)
        self.client.post(reverse("inventario:actualizar_carrito", args=[item.id]), {"cantidad": "999"})
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 1)

    def test_crear_pedido_vacia_carrito_y_envia_correo(self):
        self.login(self.cliente)
        self._agregar_al_carrito()
        mail.outbox.clear()
        r = self.client.post(reverse("inventario:crear_pedido"), self._datos_confirmacion())
        self.assertRedirects(r, reverse("inventario:pedidos"))
        self.assertEqual(Pedido.objects.filter(usuario=self.cliente).count(), 1)
        self.assertEqual(Carrito.objects.filter(usuario=self.cliente).count(), 0)
        self.assertEqual(len(mail.outbox), 1)
        # El pedido no descuenta stock hasta que se pague
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)

    def test_crear_pedido_detecta_cambio_de_precio(self):
        self.login(self.cliente)
        self._agregar_al_carrito()
        datos = self._datos_confirmacion()
        # El admin cambió el precio mientras el cliente compraba
        Producto.objects.filter(pk=self.producto.pk).update(precio=Decimal("30000"))
        r = self.client.post(reverse("inventario:crear_pedido"), datos)
        self.assertRedirects(r, reverse("inventario:carrito"))
        self.assertEqual(Pedido.objects.count(), 0)

    def test_crear_pedido_carrito_vacio(self):
        self.login(self.cliente)
        r = self.client.post(reverse("inventario:crear_pedido"), {})
        self.assertRedirects(r, reverse("inventario:carrito"))
        self.assertEqual(Pedido.objects.count(), 0)

    def test_pago_descuenta_stock_y_registra_contabilidad(self):
        self.login(self.cliente)
        self._agregar_al_carrito()
        self._agregar_al_carrito()
        self.client.post(reverse("inventario:crear_pedido"), self._datos_confirmacion())
        pedido = Pedido.objects.get(usuario=self.cliente)

        self.client.post(reverse("inventario:registrar_pago", args=[pedido.id]), {"metodo": "Efectivo"})

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 8)
        pago = Pago.objects.get(pedido=pedido)
        self.assertEqual(pago.valor, Decimal("50000.00"))
        self.assertTrue(MovimientoInventario.objects.filter(producto=self.producto, tipo="Salida", cantidad=2).exists())
        self.assertTrue(MovimientoContable.objects.filter(pedido=pedido, tipo="Ingreso", valor=Decimal("50000.00")).exists())

    def test_no_doble_pago(self):
        self.login(self.cliente)
        self._agregar_al_carrito()
        self.client.post(reverse("inventario:crear_pedido"), self._datos_confirmacion())
        pedido = Pedido.objects.get(usuario=self.cliente)
        self.client.post(reverse("inventario:registrar_pago", args=[pedido.id]), {"metodo": "Efectivo"})
        self.client.post(reverse("inventario:registrar_pago", args=[pedido.id]), {"metodo": "Efectivo"})
        self.assertEqual(Pago.objects.filter(pedido=pedido).count(), 1)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 9)

    def test_pago_con_stock_insuficiente_no_debe_registrarse(self):
        # Entre crear el pedido y pagarlo, el stock bajó a cero.
        self.login(self.cliente)
        self._agregar_al_carrito()
        self.client.post(reverse("inventario:crear_pedido"), self._datos_confirmacion())
        pedido = Pedido.objects.get(usuario=self.cliente)
        Producto.objects.filter(pk=self.producto.pk).update(stock=0)

        self.client.post(reverse("inventario:registrar_pago", args=[pedido.id]), {"metodo": "Efectivo"})

        # No debería haber pago ni ingreso contable si no hay mercancía
        self.assertFalse(Pago.objects.filter(pedido=pedido).exists(),
                         "Se registró un pago de un pedido sin stock disponible")

    def test_cancelar_pedido_pagado_devuelve_stock(self):
        self.login(self.cliente)
        self._agregar_al_carrito()
        self.client.post(reverse("inventario:crear_pedido"), self._datos_confirmacion())
        pedido = Pedido.objects.get(usuario=self.cliente)
        self.client.post(reverse("inventario:registrar_pago", args=[pedido.id]), {"metodo": "Efectivo"})
        self.client.get(reverse("inventario:logout"))

        self.login(self.empleado)
        self.client.post(reverse("inventario:actualizar_estado_pedido", args=[pedido.id]), {"estado": "Cancelado"})

        pedido.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(pedido.estado, "Cancelado")
        self.assertEqual(self.producto.stock, 10)
        self.assertTrue(MovimientoContable.objects.filter(pedido=pedido, tipo="Egreso").exists())

    def test_pedido_sin_pago_no_pasa_a_enviado(self):
        pedido = Pedido.objects.create(usuario=self.cliente)
        self.login(self.empleado)
        self.client.post(reverse("inventario:actualizar_estado_pedido", args=[pedido.id]), {"estado": "Enviado"})
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, "Pendiente")

    def test_cliente_solo_ve_sus_pedidos_en_lista(self):
        Pedido.objects.create(usuario=self.cliente)
        Pedido.objects.create(usuario=self.otro_cliente)
        self.login(self.cliente)
        r = self.client.get(reverse("inventario:pedidos"))
        self.assertEqual(len(r.context["datos"].object_list), 1)


# ---------------------------------------------------------------------------
# Seguridad: acceso a registros de otros usuarios (IDOR)
# ---------------------------------------------------------------------------

class SeguridadAccesoEntreClientesTests(BaseIntshot):
    def test_cliente_no_puede_ver_detalle_de_pedido_ajeno(self):
        ajeno = Pedido.objects.create(usuario=self.otro_cliente)
        self.login(self.cliente)
        r = self.client.get(reverse("inventario:detalle_pedido", args=[ajeno.id]))
        self.assertNotEqual(r.status_code, 200, "Un cliente pudo ver el detalle del pedido de otro cliente")

    def test_cliente_no_puede_pagar_pedido_ajeno(self):
        ajeno = Pedido.objects.create(usuario=self.otro_cliente)
        DetallePedido.objects.create(pedido=ajeno, producto=self.producto, cantidad=1, precio_unitario=25000)
        self.login(self.cliente)
        self.client.post(reverse("inventario:registrar_pago", args=[ajeno.id]), {"metodo": "Efectivo"})
        self.assertFalse(Pago.objects.filter(pedido=ajeno).exists(),
                         "Un cliente pudo registrar el pago del pedido de otro cliente")

    def test_cliente_no_puede_eliminar_item_del_carrito_ajeno(self):
        item = Carrito.objects.create(usuario=self.otro_cliente, producto=self.producto, cantidad=1)
        self.login(self.cliente)
        self.client.post(reverse("inventario:eliminar_carrito", args=[item.id]))
        self.assertTrue(Carrito.objects.filter(pk=item.pk).exists(),
                        "Un cliente pudo eliminar un producto del carrito de otro cliente")

    def test_cliente_no_puede_modificar_carrito_ajeno(self):
        item = Carrito.objects.create(usuario=self.otro_cliente, producto=self.producto, cantidad=1)
        self.login(self.cliente)
        self.client.post(reverse("inventario:actualizar_carrito", args=[item.id]), {"cantidad": "5"})
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 1, "Un cliente pudo modificar el carrito de otro cliente")

    def test_detalle_pedido_inexistente_no_da_error_500(self):
        self.login(self.admin)
        r = self.client.get(reverse("inventario:detalle_pedido", args=[9999]))
        self.assertIn(r.status_code, (302, 404))

    def test_eliminar_por_get_no_esta_permitido(self):
        # Un enlace externo (GET) no debe poder borrar registros
        self.login(self.admin)
        r = self.client.get(reverse("inventario:eliminar_producto", args=[self.producto.id]))
        self.assertEqual(r.status_code, 405)
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_admin_no_puede_eliminarse_a_si_mismo(self):
        self.login(self.admin)
        self.client.post(reverse("inventario:eliminar_usuario", args=[self.admin.id]))
        self.assertTrue(Usuario.objects.filter(pk=self.admin.pk).exists())

    def test_no_degradar_al_unico_administrador(self):
        self.login(self.admin)
        datos = {
            "nombre": "Ana", "apellido": "Prueba", "correo": self.admin.correo,
            "telefono": "3001234567", "rol": "Cliente",
        }
        self.client.post(reverse("inventario:actualizar_usuario", args=[self.admin.id]), datos)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.rol, "Administrador")

    def test_cambio_de_rol_aplica_sin_volver_a_entrar(self):
        self.login(self.cliente)
        Usuario.objects.filter(pk=self.cliente.pk).update(rol="Empleado")
        r = self.client.get(reverse("inventario:productos"))
        self.assertEqual(r.status_code, 200)

    def test_usuario_eliminado_pierde_la_sesion(self):
        self.login(self.otro_cliente)
        Usuario.objects.filter(pk=self.otro_cliente.pk).delete()
        r = self.client.get(reverse("inventario:inicio"))
        self.assertRedirects(r, reverse("inventario:login"))


# ---------------------------------------------------------------------------
# Compras a proveedores
# ---------------------------------------------------------------------------

class ComprasTests(BaseIntshot):
    def setUp(self):
        super().setUp()
        self.proveedor = Proveedor.objects.create(nombre="Textiles SA", telefono="6041234567", correo="prov@test.com")

    def test_flujo_compra_completa(self):
        self.login(self.empleado)
        r = self.client.post(reverse("inventario:crear_compra"), {"proveedor": self.proveedor.id})
        self.assertRedirects(r, reverse("inventario:compras"))
        compra = Compra.objects.get()

        self.client.post(reverse("inventario:agregar_detalle_compra", args=[compra.id]),
                         {"producto": self.producto.id, "cantidad": "5", "precio_unitario": "10000"})
        detalle = DetalleCompra.objects.get(compra=compra)

        self.client.post(reverse("inventario:recibir_compra", args=[compra.id]),
                         {f"recibido_{detalle.id}": "5", f"nuevo_precio_{detalle.id}": "25000"})

        compra.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(compra.estado, "Recibida")
        self.assertEqual(self.producto.stock, 15)
        self.assertTrue(MovimientoInventario.objects.filter(producto=self.producto, tipo="Entrada", cantidad=5).exists())
        egreso = MovimientoContable.objects.get(compra=compra)
        self.assertEqual(egreso.valor, Decimal("50000.00"))

    def test_recepcion_parcial(self):
        self.login(self.empleado)
        compra = Compra.objects.create(proveedor=self.proveedor)
        detalle = DetalleCompra.objects.create(compra=compra, producto=self.producto, cantidad=10, precio_unitario=1000)
        self.client.post(reverse("inventario:recibir_compra", args=[compra.id]),
                         {f"recibido_{detalle.id}": "4", f"nuevo_precio_{detalle.id}": "25000"})
        compra.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(compra.estado, "Recibida parcialmente")
        self.assertEqual(self.producto.stock, 14)
        self.assertEqual(MovimientoContable.objects.get(compra=compra).valor, Decimal("4000.00"))

    def test_no_recibir_mas_de_lo_pedido(self):
        self.login(self.empleado)
        compra = Compra.objects.create(proveedor=self.proveedor)
        detalle = DetalleCompra.objects.create(compra=compra, producto=self.producto, cantidad=10, precio_unitario=1000)
        r = self.client.post(reverse("inventario:recibir_compra", args=[compra.id]),
                             {f"recibido_{detalle.id}": "11", f"nuevo_precio_{detalle.id}": "25000"})
        self.assertEqual(r.status_code, 200)
        compra.refresh_from_db()
        self.assertEqual(compra.estado, "Pendiente")

    def test_no_recibir_dos_veces(self):
        self.login(self.empleado)
        compra = Compra.objects.create(proveedor=self.proveedor, estado="Recibida")
        r = self.client.get(reverse("inventario:recibir_compra", args=[compra.id]))
        self.assertRedirects(r, reverse("inventario:compras"))

    def test_no_eliminar_proveedor_con_compras(self):
        self.login(self.empleado)
        Compra.objects.create(proveedor=self.proveedor)
        self.client.post(reverse("inventario:eliminar_proveedor", args=[self.proveedor.id]))
        self.assertTrue(Proveedor.objects.filter(pk=self.proveedor.pk).exists())


# ---------------------------------------------------------------------------
# Contabilidad y configuración
# ---------------------------------------------------------------------------

class ContabilidadConfiguracionTests(BaseIntshot):
    def test_contabilidad_balance(self):
        MovimientoContable.objects.create(tipo="Ingreso", valor=100000, descripcion="a")
        MovimientoContable.objects.create(tipo="Egreso", valor=30000, descripcion="b")
        self.login(self.admin)
        r = self.client.get(reverse("inventario:contabilidad"))
        self.assertEqual(r.context["balance"], Decimal("70000"))

    def test_actualizar_configuracion(self):
        self.login(self.admin)
        datos = {
            "nombre_empresa": "Mi Tienda", "hero_titulo": "T", "hero_texto": "X",
            "titulo_catalogo": "C", "titulo_caracteristicas": "Ca", "titulo_beneficios": "B",
            "texto_footer": "F", "telefono": "3001234567", "correo": "info@test.com",
            "direccion": "Calle 1", "limite_stock_bajo": "3",
        }
        self.client.post(reverse("inventario:actualizar_configuracion"), datos)
        r = self.client.get(reverse("inventario:landing"))
        self.assertContains(r, "Mi Tienda")


# ---------------------------------------------------------------------------
# API REST
# ---------------------------------------------------------------------------

class ApiTests(BaseIntshot):
    def test_api_productos_requiere_autenticacion(self):
        r = self.client.get("/api/v1/productos/")
        self.assertIn(r.status_code, (401, 403))

    def test_api_usuarios_requiere_autenticacion(self):
        r = self.client.get("/api/v1/usuarios/")
        self.assertIn(r.status_code, (401, 403))

    def test_sesion_web_no_da_acceso_a_api(self):
        # La sesión de la web (session["logueado"]) es independiente de la API
        self.login(self.admin)
        r = self.client.get("/api/v1/pagos/")
        self.assertIn(r.status_code, (401, 403))

    def test_docs_api_cargan(self):
        r = self.client.get("/api/schema/")
        self.assertEqual(r.status_code, 200)

    def test_token_api_dura_los_dias_configurados(self):
        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token
        User.objects.create_user("api", "api@test.com", "clave12345")

        r = self.client.post("/api/api-token-auth/", {"username": "api", "password": "clave12345"})
        self.assertEqual(r.status_code, 200)
        token = r.json()["token"]
        self.assertIn("expira", r.json())

        r = self.client.get("/api/v1/productos/", HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(r.status_code, 200)

        # Un token con 29 días sigue sirviendo, con 31 ya no
        Token.objects.filter(key=token).update(created=timezone.now() - timedelta(days=29))
        r = self.client.get("/api/v1/productos/", HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(r.status_code, 200)

        Token.objects.filter(key=token).update(created=timezone.now() - timedelta(days=31))
        r = self.client.get("/api/v1/productos/", HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(r.status_code, 401)

        # Al volver a pedir token se entrega uno nuevo y vigente
        r = self.client.post("/api/api-token-auth/", {"username": "api", "password": "clave12345"})
        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(r.json()["token"], token)
