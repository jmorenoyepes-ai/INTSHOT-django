from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Sum
from .models import *
from .utilidades import *


# Página de inicio pública (landing)

def landing(request):
    # Todo el contenido de esta página se lee desde la base de datos
    configuracion = obtener_configuracion()

    # Se muestran solo los primeros 8 productos, el resto en el catálogo completo
    productos = Producto.objects.filter(stock__gt=0).order_by("nombre")[:8]

    contexto = {
        "configuracion": configuracion,
        "vinetas": Vineta.objects.all().order_by("orden"),
        "caracteristicas": Caracteristica.objects.all().order_by("orden"),
        "beneficios": Beneficio.objects.all().order_by("orden"),
        "productos": productos,
    }
    return render(request, "landing.html", contexto)


def catalogo_publico(request):
    # Catálogo que puede ver cualquier persona sin iniciar sesión
    buscar = request.GET.get("buscar", "")
    categoria = request.GET.get("categoria", "")
    t = Producto.objects.filter(stock__gt=0).order_by("nombre")
    if buscar:
        t = t.filter(nombre__icontains=buscar) | t.filter(descripcion__icontains=buscar) | t.filter(color__icontains=buscar)
        t = t.distinct()
    if categoria:
        t = t.filter(categoria=categoria)

    contexto = {
        "datos": paginar(request, t, 12),
        "filtros": parametros_url(request),
        "buscar": buscar,
        "categoria": categoria,
        "categorias": Producto.CATEGORIAS,
    }
    return render(request, "Catalogo/catalogo_publico.html", contexto)


def comprar_producto(request, id):
    # Botón "Agregar al carrito" de la página pública.
    # Si la persona no ha iniciado sesión se le pide que lo haga primero.
    if not request.session.get("logueado", False):
        messages.warning(request, "Debes iniciar sesión para poder comprar")
        return redirect("inventario:login")

    return redirect("inventario:agregar_carrito", id=id)


def login(request):
    if request.method == "POST":
        usuario = request.POST.get("user")
        clave = request.POST.get("password")

        # Validaciones del formulario
        errores = []
        if campo_vacio(usuario):
            errores.append("Debe digitar el correo")
        if campo_vacio(clave):
            errores.append("Debe digitar la contraseña")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Login/login.html", contexto)

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
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')
        veri_password = request.POST.get('veri_password')

        # Validaciones del formulario
        errores = []
        if not solo_letras(nombre):
            errores.append("El nombre es obligatorio y solo puede tener letras")
        if not solo_letras(apellido):
            errores.append("El apellido es obligatorio y solo puede tener letras")
        if not correo_valido(correo):
            errores.append("El correo no es válido. Ejemplo: nombre@correo.com")
        elif Usuario.objects.filter(correo=correo).exists():
            errores.append("Ya existe un usuario registrado con ese correo")
        if not solo_numeros(telefono):
            errores.append("El teléfono es obligatorio y solo puede tener números")
        elif len(telefono.strip()) < 7:
            errores.append("El teléfono debe tener mínimo 7 números")
        if campo_vacio(password) or len(password) < 5:
            errores.append("La contraseña debe tener mínimo 5 caracteres")
        elif password != veri_password:
            errores.append("Las contraseñas no coinciden")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Login/registro_formulario.html", contexto)

        try:
            t = Usuario(
                nombre = nombre,
                apellido = apellido,
                correo = correo,
                telefono = telefono,
                password = password,
            )
            t.save()
            messages.success(request, "Usuario guardado con éxito!!!")
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
    # La página de inicio también se arma con la información de la base de datos
    contexto = {
        "vinetas": Vineta.objects.all().order_by("orden"),
        "caracteristicas": Caracteristica.objects.all().order_by("orden"),
        "beneficios": Beneficio.objects.all().order_by("orden"),
    }
    return render(request, "index.html", contexto)


@autorizacion()
def base(request):
    return render(request, "base.html")


# CRUD de usuarios

@autorizacion(["Administrador"])
def ver_usuarios(request):
    buscar = request.GET.get("buscar", "")
    rol = request.GET.get("rol", "")
    t = Usuario.objects.all().order_by("id")
    if buscar:
        t = t.filter(nombre__icontains=buscar) | t.filter(apellido__icontains=buscar) | t.filter(correo__icontains=buscar)
        t = t.distinct()
    if rol:
        t = t.filter(rol=rol)
    contexto = {
        "datos": paginar(request, t, 10),
        "filtros": parametros_url(request),
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
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        rol = request.POST.get('rol')
        password = request.POST.get('password')
        veri_password = request.POST.get('veri_password')

        # Validaciones del formulario
        errores = []
        if not solo_letras(nombre):
            errores.append("El nombre es obligatorio y solo puede tener letras")
        if not solo_letras(apellido):
            errores.append("El apellido es obligatorio y solo puede tener letras")
        if not correo_valido(correo):
            errores.append("El correo no es válido. Ejemplo: nombre@correo.com")
        elif Usuario.objects.filter(correo=correo).exists():
            errores.append("Ya existe un usuario registrado con ese correo")
        if not solo_numeros(telefono):
            errores.append("El teléfono es obligatorio y solo puede tener números")
        elif len(telefono.strip()) < 7:
            errores.append("El teléfono debe tener mínimo 7 números")
        if campo_vacio(rol):
            errores.append("Debe seleccionar el rol del usuario")
        if campo_vacio(password) or len(password) < 5:
            errores.append("La contraseña debe tener mínimo 5 caracteres")
        elif password != veri_password:
            errores.append("Las contraseñas no coinciden")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Usuario/formulario_usuario.html", contexto)

        try:
            t = Usuario(
                nombre = nombre,
                apellido = apellido,
                correo = correo,
                telefono = telefono,
                rol = rol,
                password = password,
            )
            t.save()
            messages.success(request, "Usuario guardado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:usuarios')

    else:
        return render(request, "Usuario/formulario_usuario.html")

@autorizacion(["Administrador"])
def actualizar_usuario(request, id):
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        rol = request.POST.get('rol')

        # Validaciones del formulario
        errores = []
        if not solo_letras(nombre):
            errores.append("El nombre es obligatorio y solo puede tener letras")
        if not solo_letras(apellido):
            errores.append("El apellido es obligatorio y solo puede tener letras")
        if not correo_valido(correo):
            errores.append("El correo no es válido. Ejemplo: nombre@correo.com")
        elif Usuario.objects.filter(correo=correo).exclude(pk=id).exists():
            errores.append("Ya existe otro usuario registrado con ese correo")
        if not solo_numeros(telefono):
            errores.append("El teléfono es obligatorio y solo puede tener números")
        elif len(telefono.strip()) < 7:
            errores.append("El teléfono debe tener mínimo 7 números")
        if campo_vacio(rol):
            errores.append("Debe seleccionar el rol del usuario")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Usuario/formulario_usuario.html", contexto)

        try:
            q = Usuario.objects.get(pk = id)
            q.nombre = nombre
            q.apellido = apellido
            q.correo = correo
            q.telefono = telefono
            q.rol = rol

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
    t = Producto.objects.all().order_by("id")
    if buscar:
        t = t.filter(nombre__icontains=buscar) | t.filter(color__icontains=buscar) | t.filter(descripcion__icontains=buscar)
        t = t.distinct()
    if categoria:
        t = t.filter(categoria=categoria)
    contexto = {
        "datos": paginar(request, t, 10),
        "filtros": parametros_url(request),
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
        q.delete()

        # Eliminar físicamente la imagen de media/
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
        nombre = request.POST.get('nombre')
        color = request.POST.get('color')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        talla = request.POST.get('talla')
        stock = request.POST.get('stock')
        precio = request.POST.get('precio')

        # Validaciones del formulario
        errores = validar_producto(nombre, color, descripcion, categoria, talla, stock, precio)

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Inventarios/formulario_producto.html", contexto)

        try:
            t = Producto(
                nombre = nombre,
                color = color,
                descripcion = descripcion,
                categoria = categoria,
                talla = talla,
                stock = stock,
                precio = precio
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
        nombre = request.POST.get('nombre')
        color = request.POST.get('color')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        talla = request.POST.get('talla')
        stock = request.POST.get('stock')
        precio = request.POST.get('precio')

        # Validaciones del formulario
        errores = validar_producto(nombre, color, descripcion, categoria, talla, stock, precio)

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Inventarios/formulario_producto.html", contexto)

        try:
            q = Producto.objects.get(pk=id)

            q.nombre = nombre
            q.color = color
            q.descripcion = descripcion
            q.categoria = categoria
            q.talla = talla
            q.stock = stock
            q.precio = precio

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


def validar_producto(nombre, color, descripcion, categoria, talla, stock, precio):
    # Validaciones que usan el formulario de crear y el de actualizar producto
    errores = []

    if campo_vacio(nombre):
        errores.append("El nombre del producto es obligatorio")
    if campo_vacio(color):
        errores.append("El color del producto es obligatorio")
    if campo_vacio(descripcion):
        errores.append("La descripción del producto es obligatoria")

    if campo_vacio(categoria):
        errores.append("Debe seleccionar la categoría del producto")

    if not es_numero(stock):
        errores.append("El stock debe ser un número")
    elif int(float(stock)) < 0:
        errores.append("El stock no puede ser negativo")

    if not es_numero(precio):
        errores.append("El precio debe ser un número")
    elif float(precio) <= 0:
        errores.append("El precio debe ser mayor que cero")

    return errores


# CRUD de Proveedores

@autorizacion(["Administrador", "Empleado"])
def ver_proveedores(request):
    buscar = request.GET.get("buscar", "")
    t = Proveedor.objects.all().order_by("id")
    if buscar:
        t = t.filter(nombre__icontains=buscar) | t.filter(correo__icontains=buscar) | t.filter(telefono__icontains=buscar)
        t = t.distinct()
    contexto = {
        "datos": paginar(request, t, 10),
        "filtros": parametros_url(request),
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
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        correo = request.POST.get('correo')

        # Validaciones del formulario
        errores = []
        if campo_vacio(nombre):
            errores.append("El nombre del proveedor es obligatorio")
        if not solo_numeros(telefono):
            errores.append("El teléfono es obligatorio y solo puede tener números")
        elif len(telefono.strip()) < 7:
            errores.append("El teléfono debe tener mínimo 7 números")
        if not correo_valido(correo):
            errores.append("El correo no es válido. Ejemplo: nombre@correo.com")
        elif Proveedor.objects.filter(correo=correo).exists():
            errores.append("Ya existe un proveedor registrado con ese correo")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Proveedor/formulario_proveedor.html", contexto)

        try:
            t = Proveedor(
                nombre = nombre,
                telefono = telefono,
                correo = correo,
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
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        correo = request.POST.get('correo')

        # Validaciones del formulario
        errores = []
        if campo_vacio(nombre):
            errores.append("El nombre del proveedor es obligatorio")
        if not solo_numeros(telefono):
            errores.append("El teléfono es obligatorio y solo puede tener números")
        elif len(telefono.strip()) < 7:
            errores.append("El teléfono debe tener mínimo 7 números")
        if not correo_valido(correo):
            errores.append("El correo no es válido. Ejemplo: nombre@correo.com")
        elif Proveedor.objects.filter(correo=correo).exclude(pk=id).exists():
            errores.append("Ya existe otro proveedor registrado con ese correo")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Proveedor/formulario_proveedor.html", contexto)

        try:
            q = Proveedor.objects.get(pk = id)
            q.nombre = nombre
            q.telefono = telefono
            q.correo = correo
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
    t = Producto.objects.filter(stock__gt=0).order_by("nombre")
    if buscar:
        t = t.filter(nombre__icontains=buscar) | t.filter(descripcion__icontains=buscar) | t.filter(color__icontains=buscar)
        t = t.distinct()
    if categoria:
        t = t.filter(categoria=categoria)
    contexto = {
        "datos": paginar(request, t, 12),
        "filtros": parametros_url(request),
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

        messages.success(request, f"Producto '{producto.nombre}' agregado al carrito")
    except Producto.DoesNotExist:
        messages.warning(request, "El producto ya no está disponible")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:catalogo")

@autorizacion(["Cliente"])
def eliminar_carrito(request, id):
    try:
        q = Carrito.objects.get(pk=id)
        nombre_producto = q.producto.nombre
        q.delete()
        messages.success(request, f"Producto '{nombre_producto}' eliminado del carrito")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:carrito")

@autorizacion(["Cliente"])
def actualizar_carrito(request, id):
    try:
        q = Carrito.objects.get(pk=id)
        cantidad = request.POST.get("cantidad")

        # Validaciones del formulario
        errores = []
        if not es_numero(cantidad):
            errores.append("La cantidad debe ser un número")
        elif int(float(cantidad)) < 1:
            errores.append("La cantidad debe ser mínimo 1")
        elif int(float(cantidad)) > q.producto.stock:
            errores.append(f"Solo hay {q.producto.stock} unidades de '{q.producto.nombre}'")

        if errores:
            mostrar_errores(request, errores)
            return redirect("inventario:carrito")

        q.cantidad = int(float(cantidad))
        q.save()
        messages.success(request, f"Cantidad de '{q.producto.nombre}' actualizada")
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
        "datos": paginar(request, t, 10),
        "filtros": parametros_url(request),
        "estado": estado,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "estados": Pedido.ESTADOS,
    }
    return render(request, "Pedido/pedidos.html", contexto)

@autorizacion(["Cliente"])
def crear_pedido(request):
    if request.method != "POST":
        return redirect("inventario:carrito")

    try:
        usuario = Usuario.objects.get(pk=request.session["logueado"]["id"])
        carrito = Carrito.objects.filter(usuario=usuario)

        # Lo que el cliente estaba viendo en el carrito al dar "Confirmar Pedido"
        items_vistos = request.POST.getlist("item_visto")
        nombres_vistos = request.POST.getlist("nombre_visto")
        colores_vistos = request.POST.getlist("color_visto")
        descripciones_vistas = request.POST.getlist("descripcion_vista")
        tallas_vistas = request.POST.getlist("talla_vista")
        categorias_vistas = request.POST.getlist("categoria_vista")
        precios_vistos = request.POST.getlist("precio_visto")

        eliminados = []
        modificados = []

        for posicion in range(len(items_vistos)):
            item = Carrito.objects.filter(pk=items_vistos[posicion], usuario=usuario).first()

            # El administrador eliminó el producto mientras el cliente compraba
            if not item:
                eliminados.append(nombres_vistos[posicion])
                continue

            # El administrador editó el producto mientras el cliente compraba
            visto = {
                "nombre": nombres_vistos[posicion],
                "color": colores_vistos[posicion],
                "descripcion": descripciones_vistas[posicion],
                "talla": tallas_vistas[posicion],
                "categoria": categorias_vistas[posicion],
                "precio": precios_vistos[posicion],
            }

            cambios = buscar_cambios_producto(item.producto, visto)

            if cambios:
                modificados.append({
                    "nombre": nombres_vistos[posicion],
                    "cambios": cambios,
                })

        # Si el administrador modificó algún producto no se genera el pedido todavía.
        # Se le informa al cliente y vuelve al carrito con la información actualizada
        # para que revise y confirme de nuevo.
        if modificados:
            for nombre in eliminados:
                messages.warning(request, f"El producto '{nombre}' ya no está disponible en la tienda")

            for m in modificados:
                messages.warning(request, f"El producto '{m['nombre']}' fue modificado mientras estabas comprando: {', '.join(m['cambios'])}")

            messages.info(request, "Tu pedido NO se generó. Revisa tu carrito con la información actualizada y confirma de nuevo.")
            return redirect("inventario:carrito")

        if not carrito:
            if eliminados:
                for nombre in eliminados:
                    messages.warning(request, f"El producto '{nombre}' ya no está disponible en la tienda")
                messages.warning(request, "Tu carrito quedó vacío, por eso no se generó el pedido")
            else:
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

        # Primero se avisa de los productos que no se pudieron incluir
        for nombre in eliminados:
            messages.warning(request, f"El producto '{nombre}' ya no está disponible en la tienda y NO fue incluido en tu pedido")

        messages.success(request, "Pedido generado correctamente. Recuerda realizar el pago para confirmarlo.")

    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("inventario:pedidos")


def buscar_cambios_producto(producto, visto):
    # Compara lo que el cliente tenía en pantalla contra lo que hay ahora en la base de datos
    cambios = []

    if visto["nombre"] != producto.nombre:
        cambios.append(f"el nombre pasó de '{visto['nombre']}' a '{producto.nombre}'")

    if visto["color"] != producto.color:
        cambios.append(f"el color pasó de '{visto['color']}' a '{producto.color}'")

    if visto["descripcion"] != producto.descripcion:
        cambios.append("cambió la descripción")

    if visto["talla"] != producto.talla:
        cambios.append(f"la talla pasó de '{visto['talla']}' a '{producto.talla}'")

    if visto["categoria"] != producto.categoria:
        cambios.append(f"la categoría pasó de '{visto['categoria']}' a '{producto.categoria}'")

    if es_numero(visto["precio"]):
        if float(visto["precio"]) != float(producto.precio):
            cambios.append(f"el precio pasó de {formato_pesos(visto['precio'])} a {formato_pesos(producto.precio)}")

    return cambios


@autorizacion(["Empleado", "Administrador"])
def actualizar_estado_pedido(request, id):
    try:
        q = Pedido.objects.get(pk=id)
        nuevo_estado = request.POST.get("estado")

        # Validaciones del formulario
        estados_validos = []
        for val, label in Pedido.ESTADOS:
            estados_validos.append(val)

        if nuevo_estado not in estados_validos:
            messages.error(request, "Debe seleccionar un estado válido")
            return redirect("inventario:pedidos")

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
        "datos": paginar(request, t, 10),
        "filtros": parametros_url(request),
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
        metodo = request.POST.get("metodo")

        # Validaciones del formulario
        metodos_validos = []
        for val, label in Pago.METODOS:
            metodos_validos.append(val)

        if metodo not in metodos_validos:
            messages.error(request, "Debe seleccionar un método de pago válido")
            return redirect("inventario:pedidos")

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
            metodo=metodo
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
            descripcion=f"Pago Pedido #{pedido.id} - {metodo}",
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
        "datos": paginar(request, t, 10),
        "filtros": parametros_url(request),
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
        proveedor_id = request.POST.get("proveedor")

        # Validaciones del formulario
        errores = []
        if campo_vacio(proveedor_id):
            errores.append("Debe seleccionar el proveedor")
        elif not Proveedor.objects.filter(pk=proveedor_id).exists():
            errores.append("El proveedor seleccionado no existe")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"proveedores": Proveedor.objects.all()}
            return render(request, "Compra/formulario_compra.html", contexto)

        try:
            proveedor = Proveedor.objects.get(pk=proveedor_id)
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
        producto_id = request.POST.get("producto")
        cantidad = request.POST.get("cantidad")
        precio_unitario = request.POST.get("precio_unitario")

        # Validaciones del formulario
        errores = []
        if campo_vacio(producto_id):
            errores.append("Debe seleccionar el producto")
        elif not Producto.objects.filter(pk=producto_id).exists():
            errores.append("El producto seleccionado no existe")

        if not es_numero(cantidad):
            errores.append("La cantidad debe ser un número")
        elif int(float(cantidad)) < 1:
            errores.append("La cantidad debe ser mínimo 1")

        if not es_numero(precio_unitario):
            errores.append("El precio unitario debe ser un número")
        elif float(precio_unitario) <= 0:
            errores.append("El precio unitario debe ser mayor que cero")

        if errores:
            mostrar_errores(request, errores)
            contexto = {
                "productos": Producto.objects.all(),
                "compra": Compra.objects.get(pk=id),
                "datos": request.POST
            }
            return render(request, "Compra/formulario_detalle_compra.html", contexto)

        try:
            compra = Compra.objects.get(pk=id)
            producto = Producto.objects.get(pk=producto_id)

            detalle = DetalleCompra(
                compra=compra,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )
            detalle.save()
            messages.success(request, f"Producto '{producto.nombre}' agregado a la compra")

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

    detalles = DetalleCompra.objects.filter(compra=compra)

    if request.method == "POST":

        # Validaciones del formulario
        errores = []
        for d in detalles:
            recibido = request.POST.get(f"recibido_{d.id}")
            nuevo_precio = request.POST.get(f"nuevo_precio_{d.id}")

            if not es_numero(recibido):
                errores.append(f"La cantidad recibida de '{d.producto.nombre}' debe ser un número")
            elif int(float(recibido)) < 0:
                errores.append(f"La cantidad recibida de '{d.producto.nombre}' no puede ser negativa")
            elif int(float(recibido)) > d.cantidad:
                errores.append(f"No se puede recibir más de {d.cantidad} unidades de '{d.producto.nombre}'")

            if not es_numero(nuevo_precio):
                errores.append(f"El nuevo precio de '{d.producto.nombre}' debe ser un número")
            elif float(nuevo_precio) <= 0:
                errores.append(f"El nuevo precio de '{d.producto.nombre}' debe ser mayor que cero")

        if errores:
            mostrar_errores(request, errores)
            contexto = {
                "compra": compra,
                "datos": detalles
            }
            return render(request, "Compra/recibir_compra.html", contexto)

        try:
            es_completa = True
            total_egreso = 0
            precios_actualizados = []

            for d in detalles:
                cantidad_recibida = int(float(request.POST.get(f"recibido_{d.id}")))

                d.cantidad_recibida = cantidad_recibida
                d.save()

                if cantidad_recibida < d.cantidad:
                    es_completa = False

                producto = d.producto

                # El que recibe la compra puede actualizar el precio de venta del producto
                nuevo_precio = float(request.POST.get(f"nuevo_precio_{d.id}"))
                if nuevo_precio != float(producto.precio):
                    producto.precio = nuevo_precio
                    precios_actualizados.append(producto.nombre)

                if cantidad_recibida > 0:
                    producto.stock += cantidad_recibida

                producto.save()

                if cantidad_recibida > 0:
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

            if precios_actualizados:
                messages.info(request, f"Se actualizó el precio de: {', '.join(precios_actualizados)}")

        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect("inventario:compras")

    else:
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
        "datos": paginar(request, t, 10),
        "filtros": parametros_url(request),
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
        "datos": paginar(request, movimientos, 10),
        "filtros": parametros_url(request),
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "balance": balance,
        "tipo": tipo,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
    }
    return render(request, "Contabilidad/contabilidad.html", contexto)


# Configuración de la página de inicio

@autorizacion(["Administrador"])
def ver_configuracion(request):
    contexto = {
        "datos": obtener_configuracion(),
        "vinetas": Vineta.objects.all().order_by("orden"),
        "caracteristicas": Caracteristica.objects.all().order_by("orden"),
        "beneficios": Beneficio.objects.all().order_by("orden"),
    }
    return render(request, "Configuracion/configuracion.html", contexto)

@autorizacion(["Administrador"])
def actualizar_configuracion(request):
    if request.method == "POST":
        nombre_empresa = request.POST.get("nombre_empresa")
        hero_titulo = request.POST.get("hero_titulo")
        hero_texto = request.POST.get("hero_texto")
        titulo_catalogo = request.POST.get("titulo_catalogo")
        titulo_caracteristicas = request.POST.get("titulo_caracteristicas")
        titulo_beneficios = request.POST.get("titulo_beneficios")
        texto_footer = request.POST.get("texto_footer")
        telefono = request.POST.get("telefono")
        correo = request.POST.get("correo")
        direccion = request.POST.get("direccion")

        # Validaciones del formulario
        errores = []
        if campo_vacio(nombre_empresa):
            errores.append("El nombre de la empresa es obligatorio")
        if campo_vacio(hero_titulo):
            errores.append("El título principal es obligatorio")
        if campo_vacio(hero_texto):
            errores.append("El texto principal es obligatorio")
        if campo_vacio(titulo_catalogo):
            errores.append("El título de la sección catálogo es obligatorio")
        if campo_vacio(titulo_caracteristicas):
            errores.append("El título de la sección características es obligatorio")
        if campo_vacio(titulo_beneficios):
            errores.append("El título de la sección beneficios es obligatorio")
        if not campo_vacio(telefono) and not solo_numeros(telefono):
            errores.append("El teléfono solo puede tener números")
        if not campo_vacio(correo) and not correo_valido(correo):
            errores.append("El correo no es válido. Ejemplo: nombre@correo.com")

        if errores:
            mostrar_errores(request, errores)
            return redirect("inventario:configuracion")

        try:
            q = obtener_configuracion()
            q.nombre_empresa = nombre_empresa
            q.hero_titulo = hero_titulo
            q.hero_texto = hero_texto
            q.titulo_catalogo = titulo_catalogo
            q.titulo_caracteristicas = titulo_caracteristicas
            q.titulo_beneficios = titulo_beneficios
            q.texto_footer = texto_footer
            q.telefono = telefono
            q.correo = correo
            q.direccion = direccion

            if request.FILES.get("logo"):
                q.logo = request.FILES["logo"]

            if request.FILES.get("hero_imagen"):
                q.hero_imagen = request.FILES["hero_imagen"]

            q.save()
            messages.success(request, "Configuración actualizada con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

    return redirect("inventario:configuracion")


# Viñetas de la sección principal

@autorizacion(["Administrador"])
def crear_vineta(request):
    if request.method == "POST":
        texto = request.POST.get("texto")
        orden = request.POST.get("orden")

        # Validaciones del formulario
        errores = []
        if campo_vacio(texto):
            errores.append("El texto de la viñeta es obligatorio")
        if not es_numero(orden):
            errores.append("El orden debe ser un número")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Configuracion/formulario_vineta.html", contexto)

        try:
            t = Vineta(texto=texto, orden=orden)
            t.save()
            messages.success(request, "Viñeta guardada con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect("inventario:configuracion")

    else:
        return render(request, "Configuracion/formulario_vineta.html")

@autorizacion(["Administrador"])
def actualizar_vineta(request, id):
    if request.method == "POST":
        texto = request.POST.get("texto")
        orden = request.POST.get("orden")

        # Validaciones del formulario
        errores = []
        if campo_vacio(texto):
            errores.append("El texto de la viñeta es obligatorio")
        if not es_numero(orden):
            errores.append("El orden debe ser un número")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Configuracion/formulario_vineta.html", contexto)

        try:
            q = Vineta.objects.get(pk=id)
            q.texto = texto
            q.orden = orden
            q.save()
            messages.success(request, "Viñeta actualizada con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect("inventario:configuracion")

    else:
        q = Vineta.objects.get(pk=id)
        contexto = {
            "datos": q
        }
        return render(request, "Configuracion/formulario_vineta.html", contexto)

@autorizacion(["Administrador"])
def eliminar_vineta(request, id):
    try:
        q = Vineta.objects.get(pk=id)
        q.delete()
        messages.success(request, "Viñeta eliminada!!")
    except Vineta.DoesNotExist:
        messages.warning(request, "Alerta. La viñeta no se encontró")
    except Exception as e:
        messages.error(request, f"Error al eliminar la viñeta. {e}")

    return redirect("inventario:configuracion")


# Características de la página de inicio

@autorizacion(["Administrador"])
def crear_caracteristica(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        texto = request.POST.get("texto")
        orden = request.POST.get("orden")

        # Validaciones del formulario
        errores = []
        if campo_vacio(titulo):
            errores.append("El título de la característica es obligatorio")
        if campo_vacio(texto):
            errores.append("El texto de la característica es obligatorio")
        if not es_numero(orden):
            errores.append("El orden debe ser un número")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Configuracion/formulario_caracteristica.html", contexto)

        try:
            t = Caracteristica(titulo=titulo, texto=texto, orden=orden)
            if request.FILES.get("imagen"):
                t.imagen = request.FILES["imagen"]
            t.save()
            messages.success(request, "Característica guardada con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect("inventario:configuracion")

    else:
        return render(request, "Configuracion/formulario_caracteristica.html")

@autorizacion(["Administrador"])
def actualizar_caracteristica(request, id):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        texto = request.POST.get("texto")
        orden = request.POST.get("orden")

        # Validaciones del formulario
        errores = []
        if campo_vacio(titulo):
            errores.append("El título de la característica es obligatorio")
        if campo_vacio(texto):
            errores.append("El texto de la característica es obligatorio")
        if not es_numero(orden):
            errores.append("El orden debe ser un número")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Configuracion/formulario_caracteristica.html", contexto)

        try:
            q = Caracteristica.objects.get(pk=id)
            q.titulo = titulo
            q.texto = texto
            q.orden = orden

            if request.FILES.get("imagen"):
                q.imagen = request.FILES["imagen"]

            q.save()
            messages.success(request, "Característica actualizada con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect("inventario:configuracion")

    else:
        q = Caracteristica.objects.get(pk=id)
        contexto = {
            "datos": q
        }
        return render(request, "Configuracion/formulario_caracteristica.html", contexto)

@autorizacion(["Administrador"])
def eliminar_caracteristica(request, id):
    try:
        q = Caracteristica.objects.get(pk=id)
        titulo = q.titulo
        q.delete()
        messages.success(request, f"Característica '{titulo}' eliminada!!")
    except Caracteristica.DoesNotExist:
        messages.warning(request, "Alerta. La característica no se encontró")
    except Exception as e:
        messages.error(request, f"Error al eliminar la característica. {e}")

    return redirect("inventario:configuracion")


# Beneficios de la página de inicio

@autorizacion(["Administrador"])
def crear_beneficio(request):
    if request.method == "POST":
        icono = request.POST.get("icono")
        titulo = request.POST.get("titulo")
        texto = request.POST.get("texto")
        orden = request.POST.get("orden")

        # Validaciones del formulario
        errores = []
        if campo_vacio(titulo):
            errores.append("El título del beneficio es obligatorio")
        if campo_vacio(texto):
            errores.append("El texto del beneficio es obligatorio")
        if not es_numero(orden):
            errores.append("El orden debe ser un número")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Configuracion/formulario_beneficio.html", contexto)

        try:
            t = Beneficio(icono=icono, titulo=titulo, texto=texto, orden=orden)
            t.save()
            messages.success(request, "Beneficio guardado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect("inventario:configuracion")

    else:
        return render(request, "Configuracion/formulario_beneficio.html")

@autorizacion(["Administrador"])
def actualizar_beneficio(request, id):
    if request.method == "POST":
        icono = request.POST.get("icono")
        titulo = request.POST.get("titulo")
        texto = request.POST.get("texto")
        orden = request.POST.get("orden")

        # Validaciones del formulario
        errores = []
        if campo_vacio(titulo):
            errores.append("El título del beneficio es obligatorio")
        if campo_vacio(texto):
            errores.append("El texto del beneficio es obligatorio")
        if not es_numero(orden):
            errores.append("El orden debe ser un número")

        if errores:
            mostrar_errores(request, errores)
            contexto = {"datos": request.POST}
            return render(request, "Configuracion/formulario_beneficio.html", contexto)

        try:
            q = Beneficio.objects.get(pk=id)
            q.icono = icono
            q.titulo = titulo
            q.texto = texto
            q.orden = orden
            q.save()
            messages.success(request, "Beneficio actualizado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect("inventario:configuracion")

    else:
        q = Beneficio.objects.get(pk=id)
        contexto = {
            "datos": q
        }
        return render(request, "Configuracion/formulario_beneficio.html", contexto)

@autorizacion(["Administrador"])
def eliminar_beneficio(request, id):
    try:
        q = Beneficio.objects.get(pk=id)
        titulo = q.titulo
        q.delete()
        messages.success(request, f"Beneficio '{titulo}' eliminado!!")
    except Beneficio.DoesNotExist:
        messages.warning(request, "Alerta. El beneficio no se encontró")
    except Exception as e:
        messages.error(request, f"Error al eliminar el beneficio. {e}")

    return redirect("inventario:configuracion")


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
