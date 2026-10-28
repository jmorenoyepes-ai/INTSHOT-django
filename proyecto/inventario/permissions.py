from rest_framework import permissions

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir que cualquiera lea los servicios,
    pero solo los usuarios de staff puedan modificarlos o crearlos.
    """
    def has_permission(self, request, view):
        # Permitir métodos seguros (GET, HEAD, OPTIONS) a cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return True

        # Solo permitir POST, PUT, DELETE si el usuario es staff (is_staff=True)
        return bool(request.user and request.user.is_staff)


class SoloLecturaParaClientes(permissions.BasePermission):
    """
    Los clientes de la app solo pueden leer. Para escribir usan las acciones
    propias de la vista (por ejemplo crear-desde-carrito o registrar-pago),
    que se declaran en view.acciones_cliente. El staff puede hacer de todo.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.user.is_staff:
            return True
        return getattr(view, "action", None) in getattr(view, "acciones_cliente", ())