from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Sum
from .models import *
from .utilidades import *

def landing(request):
    return render(request, "landing.html")

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


# CRUD de usuarios

@autorizacion(["Administrador"])
def ver_usuarios(request):
    buscar = request.GET.get("buscar", "")
    rol = request.GET.get("rol", "")
    t = Usuario.objects.all()
    if buscar:
        t = t.filter(nombre__icontains=buscar) | t.filter(apellido__icontains=buscar) | t.filter(correo__icontains=buscar)
        t = t.distinct()
    if rol:
        t = t.filter(rol=rol)
    contexto = {
        "datos": t,
        "buscar": buscar,
        "rol": rol,
    }
    return render(request, "Usuario/usuarios.html", contexto)

@autorizacion(["Administrador"])
def eliminar_usuario(request, id):
    try:
        q = Usuario.objects.get(pk=id)

        if q.rol == "Administrador": 
            messages.error(request, f"No se puede eliminar un usuario administrador")
            return redirect("inventario:usuarios")
        elif q.correo == "intshotadmin@gmail.com" and q.password == "intshotadmin12345":
            messages.error(request, f"No se puede eliminar el super administrador")
            return redirect("inventario:usuarios")
        else:
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

            if q.correo == "intshotadmin@gmail.com" and q.password == "intshotadmin12345":
                messages.error(request, f"No se puede editar el super administrador")
                return redirect("inventario:usuarios")
            else:
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


# CRUD de Productos

@autorizacion(["Empleado","Administrador"])
def ver_productos(request):
    buscar = request.GET.get("buscar", "")
    categoria = request.GET.get("categoria", "")
    t = Producto.objects.all()
    if buscar:
        t = t.filter(nombre__icontains=buscar) | t.filter(color__icontains=buscar) | t.filter(descripcion__icontains=buscar)
        t = t.distinct()
    if categoria:
        t = t.filter(categoria=categoria)
    contexto = {
        "datos": t,
        "buscar": buscar,
        "categoria": categoria,
        "categorias": Producto.CATEGORIAS,
    }
    return render(request, "Inventarios/productos.html", contexto)

@autorizacion(["Empleado","Administrador"])
def eliminar_producto(request, id):
    try:
        q = Producto.objects.get(pk=id)
        nombre_producto = q.nombre

        imagen = q.imagen
        # Eliminar físicamente la imagen de media/
        q.delete()
        
        if imagen:
            imagen.delete(save=False)

        messages.success(request, f"Producto '{nombre_producto}' eliminado!!")
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
            if request.FILES.get('imagen'):
                t.imagen = request.FILES['imagen']
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
            q = Producto.objects.get(pk=id)

            q.nombre = request.POST.get('nombre')
            q.color = request.POST.get('color')
            q.descripcion = request.POST.get('descripcion')
            q.categoria = request.POST.get('categoria')
            q.talla = request.POST.get('talla')
            q.stock = request.POST.get('stock')
            q.precio = request.POST.get('precio')

            # Si se subió una nueva imagen
            if request.FILES.get('imagen'):

                # Eliminar la imagen anterior
                if q.imagen:
                    q.imagen.delete(save=False)

                # Asignar la nueva imagen
                q.imagen = request.FILES['imagen']

            # Si se marcó eliminar imagen
            elif request.POST.get('eliminar_imagen'):

                if q.imagen:
                    q.imagen.delete(save=False)

                q.imagen = None

            q.save()

            messages.success(request,"Producto actualizado con éxito!!!")

        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect('inventario:productos')

    else:
        q = Producto.objects.get(pk=id)

        contexto = {
            "datos": q
        }

        return render(request,"Inventarios/formulario_producto.html",contexto)

# CRUD de Proveedores

@autorizacion(["Administrador", "Empleado"])
def ver_proveedores(request):
    buscar = request.GET.get("buscar", "")
    t = Proveedor.objects.all()
    if buscar:
        t = t.filter(nombre__icontains=buscar) | t.filter(correo__icontains=buscar) | t.filter(telefono__icontains=buscar)
        t = t.distinct()
    contexto = {
        "datos": t,
        "buscar": buscar,
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


# Catálogo 

@autorizacion(["Cliente"])
def ver_catalogo(request):
    buscar = request.GET.get("buscar", "")
    categoria = request.GET.get("categoria", "")
    t = Producto.objects.filter(stock__gt=0)
    if buscar:
        t = t.filter(nombre__icontains=buscar) | t.filter(descripcion__icontains=buscar) | t.filter(color__icontains=buscar)
        t = t.distinct()
    if categoria:
        t = t.filter(categoria=categoria)
    contexto = {
        "datos": t,
        "buscar": buscar,
        "categoria": categoria,
        "categorias": Producto.CATEGORIAS,
    }
    return render(request, "Catalogo/catalogo.html", contexto)


# Carrito

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


# Pedidos

@autorizacion()
def ver_pedidos(request):
    estado = request.GET.get("estado", "")
    fecha_desde = request.GET.get("fecha_desde", "")
    fecha_hasta = request.GET.get("fecha_hasta", "")

    if request.session["logueado"]["rol"] == "Cliente":
        usuario = Usuario.objects.get(pk=request.session["logueado"]["id"])
        t = Pedido.objects.filter(usuario=usuario).order_by("-fecha")
    else:
        t = Pedido.objects.all().order_by("-fecha")

    if estado:
        t = t.filter(estado=estado)
    if fecha_desde:
        t = t.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        t = t.filter(fecha__date__lte=fecha_hasta)

    contexto = {
        "datos": t,
        "estado": estado,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "estados": Pedido.ESTADOS,
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

        # Verificar stock antes de crear el pedido
        for item in carrito:
            if item.cantidad > item.producto.stock:
                messages.warning(request, f"No hay stock suficiente de {item.producto.nombre}")
                return redirect("inventario:carrito")

        pedido = Pedido(usuario=usuario)
        pedido.save()

        for item in carrito:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )

        carrito.delete()
        messages.success(request, "Pedido generado correctamente. Recuerda realizar el pago para confirmarlo.")

    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:pedidos")

@autorizacion(["Empleado", "Administrador"])
def actualizar_estado_pedido(request, id):
    try:
        q = Pedido.objects.get(pk=id)
        nuevo_estado = request.POST.get("estado")

        # Si se cancela un pedido que ya fue pagado, devolver stock
        if nuevo_estado == "Cancelado" and q.estado != "Cancelado":
            if q.pagado():
                detalles = DetallePedido.objects.filter(pedido=q)
                for d in detalles:
                    d.producto.stock += d.cantidad
                    d.producto.save()
                    MovimientoInventario.objects.create(
                        producto=d.producto,
                        cantidad=d.cantidad,
                        tipo="Entrada",
                        descripcion=f"Cancelación Pedido #{q.id}"
                    )
                # Registrar egreso contable por devolución
                MovimientoContable.objects.create(
                    tipo="Egreso",
                    valor=q.total(),
                    descripcion=f"Devolución por cancelación Pedido #{q.id}",
                    pedido=q
                )

        q.estado = nuevo_estado
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


# Pagos

@autorizacion(["Administrador", "Empleado"])
def ver_pagos(request):
    metodo = request.GET.get("metodo", "")
    fecha_desde = request.GET.get("fecha_desde", "")
    fecha_hasta = request.GET.get("fecha_hasta", "")
    t = Pago.objects.all().order_by("-fecha")
    if metodo:
        t = t.filter(metodo=metodo)
    if fecha_desde:
        t = t.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        t = t.filter(fecha__date__lte=fecha_hasta)
    contexto = {
        "datos": t,
        "metodo": metodo,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "metodos": Pago.METODOS,
    }
    return render(request, "Pago/pagos.html", contexto)

@autorizacion(["Cliente"])
def registrar_pago(request, id):
    try:
        pedido = Pedido.objects.get(pk=id)

        # Evitar doble pago
        if pedido.pagado():
            messages.warning(request, "Este pedido ya tiene un pago registrado.")
            return redirect("inventario:pedidos")

        # Solo se puede pagar si el pedido está Pendiente o En proceso
        if pedido.estado not in ["Pendiente", "En proceso"]:
            messages.warning(request, f"No se puede pagar un pedido en estado '{pedido.estado}'.")
            return redirect("inventario:pedidos")

        Pago.objects.create(
            pedido=pedido,
            valor=pedido.total(),
            metodo=request.POST.get("metodo")
        )

        # Al confirmar el pago, descontar el inventario
        detalles = DetallePedido.objects.filter(pedido=pedido)
        for d in detalles:
            if d.cantidad > d.producto.stock:
                messages.warning(request, f"No hay stock suficiente de {d.producto.nombre}. Contacta con nosotros.")
            d.producto.stock -= d.cantidad
            if d.producto.stock < 0:
                d.producto.stock = 0
            d.producto.save()
            MovimientoInventario.objects.create(
                producto=d.producto,
                cantidad=d.cantidad,
                tipo="Salida",
                descripcion=f"Pago Pedido #{pedido.id}"
            )

        # Registrar ingreso contable
        MovimientoContable.objects.create(
            tipo="Ingreso",
            valor=pedido.total(),
            descripcion=f"Pago Pedido #{pedido.id} - {request.POST.get('metodo')}",
            pedido=pedido
        )

        messages.success(request, "Pago registrado correctamente")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:pedidos")


# Compras a proveedores

@autorizacion(["Administrador", "Empleado"])
def ver_compras(request):
    estado = request.GET.get("estado", "")
    fecha_desde = request.GET.get("fecha_desde", "")
    fecha_hasta = request.GET.get("fecha_hasta", "")
    buscar = request.GET.get("buscar", "")
    t = Compra.objects.all().order_by("-fecha")
    if estado:
        t = t.filter(estado=estado)
    if fecha_desde:
        t = t.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        t = t.filter(fecha__date__lte=fecha_hasta)
    if buscar:
        t = t.filter(proveedor__nombre__icontains=buscar)
    contexto = {
        "datos": t,
        "estado": estado,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "buscar": buscar,
        "estados": Compra.ESTADOS,
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

    compra = Compra.objects.get(pk=id)

    if compra.estado != "Pendiente":
        messages.warning(request, "La compra ya fue recibida")
        return redirect("inventario:compras")

    if request.method == "POST":
        try:
            detalles = DetalleCompra.objects.filter(compra=compra)
            es_completa = True
            total_egreso = 0

            for d in detalles:
                campo = f"recibido_{d.id}"
                cantidad_recibida = int(request.POST.get(campo, 0))
                cantidad_recibida = max(0, min(cantidad_recibida, d.cantidad))  

                d.cantidad_recibida = cantidad_recibida
                d.save()

                if cantidad_recibida < d.cantidad:
                    es_completa = False

                if cantidad_recibida > 0:
                    producto = d.producto
                    producto.stock += cantidad_recibida
                    producto.save()

                    MovimientoInventario.objects.create(
                        producto=producto,
                        cantidad=cantidad_recibida,
                        tipo="Entrada",
                        descripcion=f"Compra #{compra.id} - recibido {cantidad_recibida}/{d.cantidad}"
                    )

                    total_egreso += cantidad_recibida * d.precio_unitario

            compra.estado = "Recibida" if es_completa else "Recibida parcialmente"
            compra.save()

            # Registrar egreso contable
            if total_egreso > 0:
                MovimientoContable.objects.create(
                    tipo="Egreso",
                    valor=total_egreso,
                    descripcion=f"Compra #{compra.id} a {compra.proveedor.nombre} - {compra.estado}",
                    compra=compra
                )

            messages.success(request, f"Compra recibida: {compra.estado}")

        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect("inventario:compras")

    else:
        detalles = DetalleCompra.objects.filter(compra=compra)
        contexto = {
            "compra": compra,
            "datos": detalles
        }
        return render(request, "Compra/recibir_compra.html", contexto)

# Movimientos de inventario

@autorizacion(["Administrador", "Empleado"])
def ver_movimientos(request):
    tipo = request.GET.get("tipo", "")
    fecha_desde = request.GET.get("fecha_desde", "")
    fecha_hasta = request.GET.get("fecha_hasta", "")
    buscar = request.GET.get("buscar", "")
    t = MovimientoInventario.objects.all().order_by("-fecha")
    if tipo:
        t = t.filter(tipo=tipo)
    if fecha_desde:
        t = t.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        t = t.filter(fecha__date__lte=fecha_hasta)
    if buscar:
        t = t.filter(producto__nombre__icontains=buscar) | t.filter(descripcion__icontains=buscar)
        t = t.distinct()
    contexto = {
        "datos": t,
        "tipo": tipo,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "buscar": buscar,
    }
    return render(request, "Inventarios/movimientos.html", contexto)

# Contabilidad

@autorizacion(["Administrador"])
def ver_contabilidad(request):
    tipo = request.GET.get("tipo", "")
    fecha_desde = request.GET.get("fecha_desde", "")
    fecha_hasta = request.GET.get("fecha_hasta", "")
    movimientos = MovimientoContable.objects.all().order_by("-fecha")
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    if fecha_desde:
        movimientos = movimientos.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        movimientos = movimientos.filter(fecha__date__lte=fecha_hasta)

    # Totales siempre sobre todos los registros (sin filtro de fechas)
    todos = MovimientoContable.objects.all()
    total_ingresos = todos.filter(tipo="Ingreso").aggregate(total=Sum("valor"))["total"] or 0
    total_egresos  = todos.filter(tipo="Egreso").aggregate(total=Sum("valor"))["total"] or 0
    balance        = total_ingresos - total_egresos

    contexto = {
        "datos": movimientos,
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "balance": balance,
        "tipo": tipo,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
    }
    return render(request, "Contabilidad/contabilidad.html", contexto)

# importar las serializaciones de los modelos
from .serializador import *

# importar el módulo de ViewSets para las vistas de las API's
from rest_framework import viewsets

from rest_framework.authentication import *
from rest_framework.permissions import *

from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema

from inventario.authentication import ExpiringTokenAuthentication
from .permissions import IsStaffOrReadOnly 


# Vistas para las APIs
class UsuarioViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    @extend_schema(
        summary="Lista de usuarios",
        description="Obtiene todos los usuarios registrados."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    @extend_schema(
        summary="Lista de productos",
        description="Obtiene todos los productos registrados."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ProveedorViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

    @extend_schema(
        summary="Lista de proveedores",
        description="Obtiene todos los proveedores registrados."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class CarritoViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer

    @extend_schema(
            summary="Lista de carritos",
            description="Obtiene todos los carritos registrados."
        )
    def list(self, request, *args, **kwargs):
            return super().list(request, *args, **kwargs)

class PedidoViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    @extend_schema(
            summary="Lista de pedidos",
            description="Obtiene todos los pedidos registrados."
        )
    def list(self, request, *args, **kwargs):
            return super().list(request, *args, **kwargs)

class DetallePedidoViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer

    @extend_schema(
        summary="Lista de detalle pedidos",
        description="Obtiene todos los detalles de pedidos registrados."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class PagoViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

    @extend_schema(
        summary="Lista de pagos",
        description="Obtiene todos los pagos registrados."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class CompraViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    @extend_schema(
        summary="Lista de compras",
        description="Obtiene todos los compras registrados."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class DetalleCompraViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = DetalleCompra.objects.all()
    serializer_class = DetalleCompraSerializer

    @extend_schema(
        summary="Lista de detalles de compras",
        description="Obtiene todos los detalles de compras registrados."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer

    @extend_schema(
        summary="Lista de movimientos de inventario",
        description="Obtiene todos los movimientos de inventario registrados."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class MovimientoContableViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = MovimientoContable.objects.all()
    serializer_class = MovimientoContableSerializer

    @extend_schema(
        summary="Lista de movimentos contables",
        description="Obtiene todos los movimientos contables registrados."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Elimina el token asociado al usuario de la petición
        request.user.auth_token.delete()
        return Response(
            {"message": "Sesión cerrada correctamente. Token destruido."}, 
            status=status.HTTP_200_OK
        )
