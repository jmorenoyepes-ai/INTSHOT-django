# urls de la app inventario

from django.urls import path
from . import views

app_name = "inventario"
urlpatterns = [
    path('', views.login, name="login"),
    
    path('inicio/', views.index, name="index"),

    path('base/', views.base, name="base"),
    # path('productos/', views.productos, name="productos"),
    # path('insumos/', views.insumos, name="insumos"),

    # módulo usuarios
    path('usuarios/', views.ver_usuarios, name="usuarios"),
    path('eliminar_usuario/<int:id>/', views.eliminar_usuario, name="eliminar_usuario"),
    path('crear_usuario/', views.crear_usuario, name="crear_usuario"),
    path('actualizar_usuario/<int:id>/', views.actualizar_usuario, name="actualizar_usuario"),

    # módulo productos
    path('productos/', views.ver_productos, name="productos"),
    path('eliminar_producto/<int:id>/', views.eliminar_producto, name="eliminar_producto"),
    path('crear_producto/', views.crear_producto, name="crear_producto"),
    path('actualizar_producto/<int:id>/', views.actualizar_producto, name="actualizar_producto"),

    # módulo insumos
    path('insumos/', views.ver_insumos, name="insumos"),
    path('eliminar_insumo/<int:id>/', views.eliminar_insumo, name="eliminar_insumo"),
    path('crear_insumo/', views.crear_insumo, name="crear_insumo"),
    path('actualizar_insumo/<int:id>/', views.actualizar_insumo, name="actualizar_insumo"),
]
