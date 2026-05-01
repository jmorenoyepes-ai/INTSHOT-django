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
    list_display = ["id", "nombre", "color", "descripcion", "categoria", "talla", "stock"]
    list_filter = ["categoria", "talla"]
    search_fields = ["nombre", "color", "categoria", "talla"]


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre", "descripcion", "tipo", "unidad_medida", "stock"]
    list_filter = ["tipo", "unidad_medida"]
    search_fields = ["nombre", "tipo", "unidad_medida"]

