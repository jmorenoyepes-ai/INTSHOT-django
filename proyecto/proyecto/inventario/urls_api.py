from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register("usuarios", views.UsuarioViewSet)
router.register("productos", views.ProductoViewSet)
router.register("proveedores", views.ProveedorViewSet)
router.register("carritos", views.CarritoViewSet)
router.register("pedidos", views.PedidoViewSet)
router.register("detallePedidos", views.DetallePedidoViewSet)
router.register("pagos", views.PagoViewSet)
router.register("compras", views.CompraViewSet)
router.register("detalleCompras", views.DetalleCompraViewSet)
router.register("movimientosInventario", views.MovimientoInventarioViewSet)
router.register("movimientosContable", views.MovimientoContableViewSet)


urlpatterns = [
    path('v1/', include(router.urls)),
]

