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
    list_display = ["id", "nombre", "telefono", "correo", ]
    list_filter = ["nombre"]
    search_fields = ["nombre", "telefono", "correo"]

