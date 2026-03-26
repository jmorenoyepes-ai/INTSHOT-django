from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from .models import *


def login(request):
    if request.method == "POST":
        usuario = request.POST.get("user")
        clave = request.POST.get("password")
        if usuario == "intshot" and clave == "123":
            messages.success(request, "Bienvenido!!!!!!!!!")
            # messages.info(request, "infooooo")
            # messages.warning(request, "alertaaaaaa")
            # messages.error(request, "no es un error, es una prueba...")
            return redirect("inventario:index")
        else:
            messages.error(request, "Usuario o contraseña incorrectos...")
            return render(request, "login.html")
    else:
        return render(request, "login.html")

def index(request):

    return render(request, "index.html")

def base(request):
    
    return render(request, "base.html")

# def productos(request):
#     return render(request, "productos.html")

# def insumos(request):
#     return render(request, "insumos.html")

# CRUD de usuarios

def ver_usuarios(request):
    # consulta: traer todos los usuarios
    t = Usuario.objects.all()
    contexto = {
        "datos": t
    }
    return render(request, "Usuario/usuarios.html", contexto)

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

def crear_usuario(request):
    if request.method == "POST":
        # proceso datos
        # ('nombre', 'apellido', 'correo', 'telefono', 'rol' )
        try:
            t = Usuario(
                nombre = request.POST.get('nombre'),
                apellido = request.POST.get('apellido'), 
                correo = request.POST.get('correo'), 
                telefono = request.POST.get('telefono'),
                rol = request.POST.get('rol'), 
            )
            t.save()
            messages.success(request, "Usuario guardado con éxito!!!")
        except Exception as e:
            messages.error(request, f"Error : {e}")

        return redirect ('inventario:usuarios')

    else:
        # mostrar formulario
        return render(request, "Usuario/formulario_usuario.html")
    
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

def ver_productos(request):
    # consulta: traer todos los productos
    t = Producto.objects.all()
    contexto = {
        "datos": t
    }
    return render(request, "Inventarios/productos.html", contexto)

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

def ver_insumos(request):
    # consulta: traer todos los insumos
    t = Insumo.objects.all()
    contexto = {
        "datos": t
    }
    return render(request, "Inventarios/insumos.html", contexto)

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
