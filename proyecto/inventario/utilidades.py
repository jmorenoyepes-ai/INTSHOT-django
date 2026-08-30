from django.shortcuts import redirect
from django.contrib import messages
from django.core.paginator import Paginator

def autorizacion(roles=[]):
    def verificar_autenticacion(func):
        def envoltorio_func(request, *args, **kwargs):
            print("*"*30)
            print("Verificando login de usuario.....")
            # captura de variable de sesion
            validar = request.session.get("logueado", False)

            if validar:

                print("Usuario Autenticado, continuar...")
                print("Verificando roles:")
                if roles!= [] and validar["rol"] not in roles:
                    messages.warning(request, "No tienes permiso para éste módulo....")
                    return redirect("inventario:inicio")
                return func(request, *args, **kwargs)
            else:
                print("Usuario no logueado.. redirigir a landing")
                return redirect("inventario:login")
        return envoltorio_func
    return verificar_autenticacion

# Validaciones sencillas para los formularios

def campo_vacio(valor):
    # Devuelve True si el campo llegó vacío o solo con espacios
    if valor is None:
        return True
    if valor.strip() == "":
        return True
    return False


def solo_letras(valor):
    # Devuelve True si el texto solo tiene letras y espacios (nombres, apellidos)
    if campo_vacio(valor):
        return False
    texto = valor.replace(" ", "")
    return texto.isalpha()


def solo_numeros(valor):
    # Devuelve True si el texto solo tiene números (teléfonos)
    if campo_vacio(valor):
        return False
    return valor.strip().isdigit()


def es_numero(valor):
    # Devuelve True si el valor se puede convertir a número
    try:
        float(valor)
        return True
    except (TypeError, ValueError):
        return False


def correo_valido(valor):
    # Un correo válido debe tener una sola @ y un punto en el dominio
    if campo_vacio(valor):
        return False
    if valor.count("@") != 1:
        return False
    nombre, dominio = valor.split("@")
    if campo_vacio(nombre) or campo_vacio(dominio):
        return False
    if "." not in dominio:
        return False
    return True


def mostrar_errores(request, errores):
    # Muestra en pantalla todos los errores encontrados en un formulario
    for error in errores:
        messages.error(request, error)


# Paginación

def paginar(request, lista, cantidad=10):
    # Divide los registros en páginas de "cantidad" elementos
    paginador = Paginator(lista, cantidad)
    numero = request.GET.get("pagina")
    return paginador.get_page(numero)


def parametros_url(request):
    # Guarda los filtros de búsqueda actuales para no perderlos al cambiar de página
    parametros = request.GET.copy()
    if "pagina" in parametros:
        del parametros["pagina"]
    return parametros.urlencode()


# Formato de dinero

def formato_pesos(valor):
    # Muestra un número como pesos colombianos. Ejemplo: 25000 -> $ 25.000
    try:
        numero = int(float(valor))
    except (TypeError, ValueError):
        return "$ 0"

    # Se separan los miles con puntos
    texto = "{:,}".format(numero).replace(",", ".")

    return f"$ {texto}"
