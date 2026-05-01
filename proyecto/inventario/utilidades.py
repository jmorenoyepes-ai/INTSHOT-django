from django.shortcuts import redirect

def verificar_autenticacion(func):
    def envoltorio_func(request, *args, **kwargs):
        print("*"*30)
        print("Verificando login de usuario.....")
        
        validar = request.session.get("logueado", False)
        if validar:
            print("Usuario Autenticado, continuar...")
            return func(request, *args, **kwargs)
        else:
            print("Usuario no logueado.. redirigir a login")
            return redirect("inventario:login")

    return envoltorio_func
