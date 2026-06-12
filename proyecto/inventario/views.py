from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from .models import *
from .utilidades import *

def login(request):
    if request.method == "POST":
        usuario = request.POST.get("user")
        clave = request.POST.get("password")
        
        try:
            q = Usuario.objects.get(correo = usuario, password = clave)
            messages.success(request, "Bienvenido!!!!!!!!!!")
            request.session["logueado"] = {
                "id" :q.id,
                "nombre": f"{q.nombre} {q.apellido}",
                "rol": q.rol
            }
            return redirect("inventario:inicio")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos...")
            request.session["logueado"] = None
            return redirect("inventario:login")
    else:
        if request.session.get("logueado", False):
            return redirect("inventario:inicio")
        else:
            return render(request, "Login/login.html")
        
def registrarse(request):
    if request.method == "POST":
        try:
            if request.POST.get('password') == request.POST.get('veri_password'):
                t = Usuario(
                    nombre = request.POST.get('nombre'),
                    apellido = request.POST.get('apellido'), 
                    correo = request.POST.get('correo'), 
                    telefono = request.POST.get('telefono'),
                    password = request.POST.get('password'),
                )
                t.save()
                messages.success(request, "Usuario guardado con éxito!!!")
            else:
                messages.error(request, "Las contraseñas no coinciden")
                return redirect ("inventario:registrarse")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:login')

    else:
        return render(request, "Login/registro_formulario.html")

@autorizacion()
def logout(request):
    try:
        del request.session["logueado"]
        messages.success(request, "Sesión cerrada!!")
        return redirect("inventario:login")
    except Exception as e:
        messages.warning(request, f"Error: {e}")
        return redirect("inventario:inicio")

@autorizacion()
def inicio(request):
    return render(request, "index.html")

@autorizacion()
def base(request):
    return render(request, "base.html")


# ─────────────────────────────────────────────
# CRUD de usuarios
# ─────────────────────────────────────────────

@autorizacion(["Administrador"])
def ver_usuarios(request):
    t = Usuario.objects.all()
    contexto = {
        "datos": t
    }
    return render(request, "Usuario/usuarios.html", contexto)

@autorizacion(["Administrador"])
def eliminar_usuario(request, id):
    try:
        q = Usuario.objects.get(pk=id)
        q.delete()
        messages.success(request, f"Usuario '{q.nombre}' eliminado!!")
    except IntegrityError:
        messages.info(request, f"No se puede eliminar el usuario porque tiene registros relacionados.")
    except Usuario.DoesNotExist:
        messages.warning(request, f"Alerta. El usuario no se encontró")
    except Exception as e:
        messages.error(request, f"Error al eliminar el usuario. {e}")
    
    return redirect("inventario:usuarios")

@autorizacion(["Administrador"])
def crear_usuario(request):
    if request.method == "POST":
        try:
            if request.POST.get('password') == request.POST.get('veri_password'):
                t = Usuario(
                    nombre = request.POST.get('nombre'),
                    apellido = request.POST.get('apellido'), 
                    correo = request.POST.get('correo'), 
                    telefono = request.POST.get('telefono'),
                    rol = request.POST.get('rol'), 
                    password = request.POST.get('password'),
                )
                t.save()
                messages.success(request, "Usuario guardado con éxito!!!")
            else:
                messages.error(request, "Las contraseñas no coinciden")
                return redirect ("inventario:crear_usuario")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:usuarios')

    else:
        return render(request, "Usuario/formulario_usuario.html")

@autorizacion(["Administrador"])
def actualizar_usuario(request, id):
    if request.method == "POST":
        try:
            q = Usuario.objects.get(pk = id)
            q.nombre = request.POST.get('nombre')
            q.apellido = request.POST.get('apellido')
            q.correo = request.POST.get('correo')
            q.telefono = request.POST.get('telefono')
            q.rol = request.POST.get('rol')
            q.save()
            messages.success(request, "Usuario actualizado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:usuarios')
        
    else:
        q = Usuario.objects.get(pk = id)
        contexto = {
            "datos" : q
        }
        return render(request, "Usuario/formulario_usuario.html", contexto)


# ─────────────────────────────────────────────
# CRUD de Productos
# ─────────────────────────────────────────────

@autorizacion(["Empleado","Administrador"])
def ver_productos(request):
    t = Producto.objects.all()
    contexto = {
        "datos": t
    }
    return render(request, "Inventarios/productos.html", contexto)

@autorizacion(["Empleado","Administrador"])
def eliminar_producto(request, id):
    try:
        q = Producto.objects.get(pk=id)
        q.delete()
        messages.success(request, f"Producto '{q.nombre}' eliminado!!")
    except IntegrityError:
        messages.info(request, f"No se puede eliminar el producto porque tiene registros relacionados.")
    except Producto.DoesNotExist:
        messages.warning(request, f"Alerta. El producto no se encontró")
    except Exception as e:
        messages.error(request, f"Error al eliminar el producto. {e}")
    
    return redirect("inventario:productos")

@autorizacion(["Empleado","Administrador"])
def crear_producto(request):
    if request.method == "POST":
        try:
            t = Producto(
                nombre = request.POST.get('nombre'),
                color = request.POST.get('color'), 
                descripcion = request.POST.get('descripcion'), 
                categoria = request.POST.get('categoria'),
                talla = request.POST.get('talla'), 
                stock = request.POST.get('stock'), 
                precio = request.POST.get('precio')
            )
            t.save()
            messages.success(request, "Producto guardado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:productos')

    else:
        return render(request, "Inventarios/formulario_producto.html")

@autorizacion(["Empleado","Administrador"])
def actualizar_producto(request, id):
    if request.method == "POST":
        try:
            q = Producto.objects.get(pk = id)
            q.nombre = request.POST.get('nombre')
            q.color = request.POST.get('color')
            q.descripcion = request.POST.get('descripcion')
            q.categoria = request.POST.get('categoria')
            q.talla = request.POST.get('talla')
            q.stock = request.POST.get('stock')
            q.precio = request.POST.get('precio')
            q.save()
            messages.success(request, "Producto actualizado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:productos')
        
    else:
        q = Producto.objects.get(pk = id)
        contexto = {
            "datos" : q
        }
        return render(request, "Inventarios/formulario_producto.html", contexto)


# ─────────────────────────────────────────────
# CRUD de Proveedores
# ─────────────────────────────────────────────

@autorizacion(["Administrador", "Empleado"])
def ver_proveedores(request):
    t = Proveedor.objects.all()
    contexto = {
        "datos": t
    }
    return render(request, "Proveedor/proveedor.html", contexto)

@autorizacion(["Administrador", "Empleado"])
def eliminar_proveedor(request, id):
    try:
        q = Proveedor.objects.get(pk=id)
        q.delete()
        messages.success(request, f"Proveedor '{q.nombre}' eliminado!!")
    except IntegrityError:
        messages.info(request, f"No se puede eliminar el proveedor porque tiene registros relacionados.")
    except Proveedor.DoesNotExist:
        messages.warning(request, f"Alerta. El proveedor no se encontró")
    except Exception as e:
        messages.error(request, f"Error al eliminar el proveedor. {e}")
    
    return redirect("inventario:proveedores")

@autorizacion(["Administrador", "Empleado"])
def crear_proveedor(request):
    if request.method == "POST":
        try:
                t = Proveedor(
                    nombre = request.POST.get('nombre'),
                    telefono = request.POST.get('telefono'),
                    correo = request.POST.get('correo'), 
                )
                t.save()
                messages.success(request, "Proveedor guardado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")
            return redirect ("inventario:crear_proveedor")

        return redirect ('inventario:proveedores')

    else:
        return render(request, "Proveedor/formulario_proveedor.html")

@autorizacion(["Administrador", "Empleado"])
def actualizar_proveedor(request, id):
    if request.method == "POST":
        try:
            q = Proveedor.objects.get(pk = id)
            q.nombre = request.POST.get('nombre')
            q.telefono = request.POST.get('telefono')
            q.correo = request.POST.get('correo')
            q.save()
            messages.success(request, "Proveedor actualizado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:proveedores')
        
    else:
        q = Proveedor.objects.get(pk = id)
        contexto = {
            "datos" : q
        }
        return render(request, "Proveedor/formulario_proveedor.html", contexto)


# ─────────────────────────────────────────────
# Catálogo (vista pública para clientes)
# ─────────────────────────────────────────────

@autorizacion(["Cliente"])
def ver_catalogo(request):
    # Solo productos con stock disponible, excluye Insumos
    t = Producto.objects.filter(stock__gt=0).exclude(categoria="Insumos")
    contexto = {
        "datos": t
    }
    return render(request, "Catalogo/catalogo.html", contexto)


# ─────────────────────────────────────────────
# Carrito
# ─────────────────────────────────────────────

@autorizacion(["Cliente"])
def ver_carrito(request):
    usuario = Usuario.objects.get(pk=request.session["logueado"]["id"])
    t = Carrito.objects.filter(usuario=usuario)
    total = sum(item.subtotal() for item in t)

    contexto = {
        "datos": t,
        "total": total
    }
    return render(request, "Carrito/carrito.html", contexto)

@autorizacion(["Cliente"])
def agregar_carrito(request, id):
    try:
        usuario = Usuario.objects.get(pk=request.session["logueado"]["id"])
        producto = Producto.objects.get(pk=id)

        q = Carrito.objects.filter(
            usuario=usuario,
            producto=producto
        ).first()

        if q:
            q.cantidad += 1
            q.save()
        else:
            Carrito.objects.create(
                usuario=usuario,
                producto=producto,
                cantidad=1
            )

        messages.success(request, "Producto agregado al carrito")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:catalogo")

@autorizacion(["Cliente"])
def eliminar_carrito(request, id):
    try:
        q = Carrito.objects.get(pk=id)
        q.delete()
        messages.success(request, "Producto eliminado del carrito")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:carrito")

@autorizacion(["Cliente"])
def actualizar_carrito(request, id):
    try:
        q = Carrito.objects.get(pk=id)
        cantidad = int(request.POST.get("cantidad", 1))
        if cantidad < 1:
            q.delete()
            messages.success(request, "Producto eliminado del carrito")
        else:
            q.cantidad = cantidad
            q.save()
            messages.success(request, "Cantidad actualizada")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:carrito")


# ─────────────────────────────────────────────
# Pedidos
# ─────────────────────────────────────────────

@autorizacion()
def ver_pedidos(request):
    if request.session["logueado"]["rol"] == "Cliente":
        usuario = Usuario.objects.get(pk=request.session["logueado"]["id"])
        t = Pedido.objects.filter(usuario=usuario).order_by("-fecha")
    else:
        t = Pedido.objects.all().order_by("-fecha")

    contexto = {
        "datos": t
    }
    return render(request, "Pedido/pedidos.html", contexto)

@autorizacion(["Cliente"])
def crear_pedido(request):
    try:
        usuario = Usuario.objects.get(pk=request.session["logueado"]["id"])
        carrito = Carrito.objects.filter(usuario=usuario)

        if not carrito:
            messages.warning(request, "El carrito está vacío")
            return redirect("inventario:carrito")

        pedido = Pedido(usuario=usuario)
        pedido.save()

        for item in carrito:
            if item.cantidad > item.producto.stock:
                messages.warning(request, f"No hay stock suficiente de {item.producto.nombre}")
                pedido.delete()
                return redirect("inventario:carrito")

            DetallePedido.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )

            item.producto.stock -= item.cantidad
            item.producto.save()

            MovimientoInventario.objects.create(
                producto=item.producto,
                cantidad=item.cantidad,
                tipo="Salida",
                descripcion=f"Pedido #{pedido.id}"
            )

        carrito.delete()
        messages.success(request, "Pedido generado correctamente")

    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:pedidos")

@autorizacion(["Empleado", "Administrador"])
def actualizar_estado_pedido(request, id):
    try:
        q = Pedido.objects.get(pk=id)
        q.estado = request.POST.get("estado")
        q.save()
        messages.success(request, "Estado actualizado")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:pedidos")

@autorizacion()
def ver_detalle_pedido(request, id):
    pedido = Pedido.objects.get(pk=id)
    detalles = DetallePedido.objects.filter(pedido=pedido)
    contexto = {
        "pedido": pedido,
        "datos": detalles
    }
    return render(request, "Pedido/detalle_pedido.html", contexto)


# ─────────────────────────────────────────────
# Pagos
# ─────────────────────────────────────────────

@autorizacion(["Administrador", "Empleado"])
def ver_pagos(request):
    t = Pago.objects.all().order_by("-fecha")
    contexto = {
        "datos": t
    }
    return render(request, "Pago/pagos.html", contexto)

@autorizacion(["Cliente"])
def registrar_pago(request, id):
    try:
        pedido = Pedido.objects.get(pk=id)
        Pago.objects.create(
            pedido=pedido,
            valor=pedido.total(),
            metodo=request.POST.get("metodo")
        )
        messages.success(request, "Pago registrado correctamente")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:pedidos")


# ─────────────────────────────────────────────
# Compras a proveedores
# ─────────────────────────────────────────────

@autorizacion(["Administrador", "Empleado"])
def ver_compras(request):
    t = Compra.objects.all().order_by("-fecha")
    contexto = {
        "datos": t
    }
    return render(request, "Compra/compras.html", contexto)

@autorizacion(["Administrador", "Empleado"])
def crear_compra(request):
    if request.method == "POST":
        try:
            proveedor = Proveedor.objects.get(pk=request.POST.get("proveedor"))
            compra = Compra(proveedor=proveedor)
            compra.save()
            messages.success(request, "Compra registrada")
        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect("inventario:compras")

    else:
        contexto = {
            "proveedores": Proveedor.objects.all()
        }
        return render(request, "Compra/formulario_compra.html", contexto)

@autorizacion(["Administrador", "Empleado"])
def ver_detalle_compra(request, id):
    compra = Compra.objects.get(pk=id)
    detalles = DetalleCompra.objects.filter(compra=compra)
    contexto = {
        "compra": compra,
        "datos": detalles
    }
    return render(request, "Compra/detalle_compra.html", contexto)

@autorizacion(["Administrador", "Empleado"])
def agregar_detalle_compra(request, id):
    if request.method == "POST":
        try:
            compra = Compra.objects.get(pk=id)
            producto = Producto.objects.get(pk=request.POST.get("producto"))

            detalle = DetalleCompra(
                compra=compra,
                producto=producto,
                cantidad=request.POST.get("cantidad"),
                precio_unitario=request.POST.get("precio_unitario")
            )
            detalle.save()
            messages.success(request, "Producto agregado a la compra")

        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect("inventario:detalle_compra", id=id)

    else:
        contexto = {
            "productos": Producto.objects.all(),
            "compra": Compra.objects.get(pk=id)
        }
        return render(request, "Compra/formulario_detalle_compra.html", contexto)

@autorizacion(["Administrador", "Empleado"])
def eliminar_detalle_compra(request, id):
    try:
        q = DetalleCompra.objects.get(pk=id)
        compra_id = q.compra.id
        q.delete()
        messages.success(request, "Producto eliminado de la compra")
        return redirect("inventario:detalle_compra", id=compra_id)

    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect("inventario:compras")

@autorizacion(["Administrador", "Empleado"])
def recibir_compra(request, id):
    try:
        compra = Compra.objects.get(pk=id)

        if compra.estado == "Recibida":
            messages.warning(request, "La compra ya fue recibida")
            return redirect("inventario:compras")

        detalles = DetalleCompra.objects.filter(compra=compra)

        for d in detalles:
            producto = d.producto
            producto.stock += d.cantidad
            producto.save()

            MovimientoInventario.objects.create(
                producto=producto,
                cantidad=d.cantidad,
                tipo="Entrada",
                descripcion=f"Compra #{compra.id}"
            )

        compra.estado = "Recibida"
        compra.save()
        messages.success(request, "Compra recibida correctamente")

    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:compras")


# ─────────────────────────────────────────────
# Movimientos de inventario
# ─────────────────────────────────────────────

@autorizacion(["Administrador", "Empleado"])
def ver_movimientos(request):
    t = MovimientoInventario.objects.all().order_by("-fecha")
    contexto = {
        "datos": t
    }
    return render(request, "Inventarios/movimientos.html", contexto)
