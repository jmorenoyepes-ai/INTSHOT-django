from django.shortcuts import redirect
from django.contrib import messages

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
                print("Usuario no logueado.. redirigir a login")
                return redirect("inventario:login")
        return envoltorio_func
    return verificar_autenticacion