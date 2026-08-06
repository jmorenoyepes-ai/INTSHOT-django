from django.contrib import admin

from .models import *

# Register your models here.
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre", "apellido", "rol", "telefono", "correo",  "password"]
    list_filter = ["rol"]
    search_fields = ["nombre", "apellido", "correo"]
    # list_editable = ["rol"]

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre", "color", "descripcion", "categoria", "talla", "stock" , "precio"]
    list_filter = ["categoria", "talla"]
    search_fields = ["nombre", "color", "categoria", "talla"]

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre", "telefono", "correo"]
    list_filter = ["nombre"]
    search_fields = ["nombre", "telefono", "correo"]

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["id", "usuario", "fecha", "estado"]
    list_filter = ["usuario"]
    search_fields = ["usuario", "fecha", "estado"]

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ["id", "pedido", "producto", "cantidad", "precio_unitario"]
    list_filter = ["pedido", "producto"]
    search_fields = ["pedido", "producto"]

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ["id", "proveedor", "fecha", "estado"]
    list_filter = ["proveedor"]
    search_fields = ["proveedor", "fecha", "estado"]

@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ["id", "compra", "producto", "cantidad", "cantidad_recibida", "precio_unitario"]
    list_filter = ["compra", "producto"]
    search_fields = ["compra", "producto"]

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ["id", "producto", "cantidad", "fecha", "descripcion", "tipo"]
    list_filter = ["producto", "fecha", "tipo"]
    search_fields = ["producto", "fecha", "tipo"]

@admin.register(MovimientoContable)
class MovimientoContableAdmin(admin.ModelAdmin):
    list_display = ["id", "fecha", "tipo", "valor"]
    list_filter = ["tipo", "fecha"]
    search_fields = ["fecha", "tipo", "valor"]



