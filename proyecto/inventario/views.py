from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from .models import *
from .utilidades import *

# def login(request):
#     if request.method == "POST":
#         usuario = request.POST.get("user")
#         clave = request.POST.get("password")
#         if usuario == "intshot" and clave == "123":
#             messages.success(request, "Bienvenido!!!!!!!!!")
#             # messages.info(request, "infooooo")
#             # messages.warning(request, "alertaaaaaa")
#             # messages.error(request, "no es un error, es una prueba...")
#             return redirect("inventario:index")
#         else:
#             messages.error(request, "Usuario o contraseña incorrectos...")
#             return render(request, "login.html")
#     else:
#         return render(request, "login.html")

def login(request):
    if request.method == "POST":
        usuario = request.POST.get("user")
        clave = request.POST.get("password")
        
        # q = select * from Trabajador where email = usuario and password = clave
        
        try:
            q = Usuario.objects.get(correo = usuario, password = clave)
            messages.success(request, "Bienvenido!!!!!!!!!")
            # variable de sesion:
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
            return render(request, "login.html")
        
def registrarse(request):
    if request.method == "POST":
        # proceso datos
        # ('nombre', 'apellido', 'correo', 'telefono', 'rol' )
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
        # mostrar formulario
        return render(request, "registro_formulario.html")

@verificar_autenticacion
def logout(request):
    try:
        del request.session["logueado"]
        messages.success(request, "Sesión cerrada!!")
        return redirect("inventario:login")
    except Exception as e:
        messages.warning(request, f"Error: {e}")
        return redirect("inventario:inicio")

@verificar_autenticacion
def inicio(request):

    return render(request, "index.html")

@verificar_autenticacion
def base(request):
    
    return render(request, "base.html")

# CRUD de usuarios
@verificar_autenticacion
def ver_usuarios(request):
    # consulta: traer todos los usuarios
    t = Usuario.objects.all()
    contexto = {
        "datos": t
    }
    return render(request, "Usuario/usuarios.html", contexto)

@verificar_autenticacion
def eliminar_usuario(request, id):
    # a = SELECT * FROM Usuario where id=id
    # del a
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

@verificar_autenticacion
def crear_usuario(request):
    if request.method == "POST":
        # proceso datos
        # ('nombre', 'apellido', 'correo', 'telefono', 'rol' )
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
        # mostrar formulario
        return render(request, "Usuario/formulario_usuario.html")

@verificar_autenticacion
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


# CRUD de Productos
@verificar_autenticacion
def ver_productos(request):
    # consulta: traer todos los productos
    t = Producto.objects.all()
    contexto = {
        "datos": t
    }
    return render(request, "Inventarios/productos.html", contexto)

@verificar_autenticacion
def eliminar_producto(request, id):
    # a = SELECT * FROM Producto where id=id
    # del a
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

@verificar_autenticacion
def crear_producto(request):
    if request.method == "POST":
        # proceso datos
        # ('nombre', 'color', 'descripcion', 'categoria', 'talla', 'stock', )
        try:
            t = Producto(
                nombre = request.POST.get('nombre'),
                color = request.POST.get('color'), 
                descripcion = request.POST.get('descripcion'), 
                categoria = request.POST.get('categoria'),
                talla = request.POST.get('talla'), 
                stock = request.POST.get('stock'), 
            )
            t.save()
            messages.success(request, "Producto guardado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:productos')

    else:
        # mostrar formulario
        return render(request, "Inventarios/formulario_producto.html")

@verificar_autenticacion
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

# CRUD de Insumos
@verificar_autenticacion
def ver_insumos(request):
    # consulta: traer todos los insumos
    t = Insumo.objects.all()
    contexto = {
        "datos": t
    }
    return render(request, "Inventarios/insumos.html", contexto)

@verificar_autenticacion
def eliminar_insumo(request, id):
    # a = SELECT * FROM Insumo where id=id
    # del a
    try:
        q = Insumo.objects.get(pk=id)
        q.delete()
        messages.success(request, f"Insumo '{q.nombre}' eliminado!!")
    except IntegrityError:
        messages.info(request, f"No se puede eliminar el insumo porque tiene registros relacionados.")
    except Insumo.DoesNotExist:
        messages.warning(request, f"Alerta. El insumo no se encontró")
    except Exception as e:
        messages.error(request, f"Error al eliminar el insumo. {e}")
    
    return redirect("inventario:insumos")

@verificar_autenticacion
def crear_insumo(request):
    if request.method == "POST":
        # proceso datos
        # ('nombre', 'descripcion', 'tipo', 'unidad_medida', 'stock', )
        try:
            t = Insumo(
                nombre = request.POST.get('nombre'),
                descripcion = request.POST.get('descripcion'), 
                tipo = request.POST.get('tipo'), 
                unidad_medida = request.POST.get('unidad_medida'),
                stock = request.POST.get('stock'), 
            )
            t.save()
            messages.success(request, "Insumo guardado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:insumos')

    else:
        # mostrar formulario
        return render(request, "Inventarios/formulario_insumo.html")

@verificar_autenticacion
def actualizar_insumo(request, id):
    
    if request.method == "POST":
        try:
            q = Insumo.objects.get(pk = id)
            q.nombre = request.POST.get('nombre')
            q.descripcion = request.POST.get('descripcion')
            q.tipo = request.POST.get('tipo')
            q.unidad_medida = request.POST.get('unidad_medida')
            q.stock = request.POST.get('stock')
            q.save()
            messages.success(request, "Insumo actualizado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:insumos')
        
    else:
        q = Insumo.objects.get(pk = id)
        contexto = {
            "datos" : q
        }
        return render(request, "Inventarios/formulario_insumo.html", contexto)
