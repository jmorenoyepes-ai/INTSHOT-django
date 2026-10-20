from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.core.cache import cache
from django.conf import settings


def autorizacion(roles=[]):
    # Decorador que protege las vistas privadas.
    # - Si no hay sesión, manda al login.
    # - Si el usuario fue eliminado, cierra la sesión.
    # - El rol se vuelve a leer de la base de datos en cada petición, así un
    #   cambio de rol hecho por el administrador aplica de inmediato.
    def verificar_autenticacion(func):
        def envoltorio_func(request, *args, **kwargs):
            from .models import Usuario

            sesion = request.session.get("logueado", False)
            if not sesion:
                return redirect("inventario:login")

            usuario = Usuario.objects.filter(pk=sesion.get("id")).first()
            if not usuario:
                request.session.pop("logueado", None)
                messages.warning(request, "Tu cuenta ya no existe. Inicia sesión de nuevo.")
                return redirect("inventario:login")

            if usuario.rol != sesion.get("rol"):
                sesion["rol"] = usuario.rol
                sesion["nombre"] = f"{usuario.nombre} {usuario.apellido}"
                request.session["logueado"] = sesion

            if roles != [] and usuario.rol not in roles:
                messages.warning(request, "No tienes permiso para éste módulo....")
                return redirect("inventario:inicio")

            return func(request, *args, **kwargs)

        envoltorio_func.__name__ = func.__name__
        envoltorio_func.__doc__ = func.__doc__
        return envoltorio_func
    return verificar_autenticacion


def usuario_logueado(request):
    # Devuelve el usuario de la sesión actual (ya validado por @autorizacion)
    from .models import Usuario
    return Usuario.objects.get(pk=request.session["logueado"]["id"])


def es_cliente(request):
    return request.session["logueado"]["rol"] == "Cliente"


# Límite de intentos de inicio de sesión (protección contra fuerza bruta)

def _clave_intentos(correo):
    return f"login_intentos:{(correo or '').strip().lower()}"


def login_bloqueado(correo):
    intentos = cache.get(_clave_intentos(correo), 0)
    return intentos >= settings.LOGIN_MAX_INTENTOS


def registrar_intento_fallido(correo):
    clave = _clave_intentos(correo)
    intentos = cache.get(clave, 0) + 1
    cache.set(clave, intentos, settings.LOGIN_BLOQUEO_MINUTOS * 60)


def limpiar_intentos(correo):
    cache.delete(_clave_intentos(correo))


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


# Contraseñas encriptadas

def password_en_texto_plano(usuario):
    # Las contraseñas nuevas se guardan con make_password (empiezan con pbkdf2_)
    return not usuario.password.startswith("pbkdf2_")


def guardar_password(usuario, clave):
    # Encripta la contraseña y la deja lista para guardar en el usuario
    usuario.password = make_password(clave)


def verificar_password(usuario, clave):
    # Compara la contraseña. Si el usuario todavía tiene la contraseña en
    # texto plano (usuarios antiguos), se compara directamente y luego se
    # encripta automáticamente al volver a iniciar sesión.
    if password_en_texto_plano(usuario):
        return usuario.password == clave
    return check_password(clave, usuario.password)
