# urls de la app inventario

from django.urls import path
from . import views

app_name = "inventario"
urlpatterns = [
    path('', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('registrarse/', views.registrarse, name="registrarse"),
    
    path('inicio/', views.inicio, name="inicio"),
    path('base/', views.base, name="base"),

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

    # módulo proveedores
    path('proveedores/', views.ver_proveedores, name="proveedores"),
    path('eliminar_proveedor/<int:id>/', views.eliminar_proveedor, name="eliminar_proveedor"),
    path('crear_proveedor/', views.crear_proveedor, name="crear_proveedor"),
    path('actualizar_proveedor/<int:id>/', views.actualizar_proveedor, name="actualizar_proveedor"),

    # módulo catálogo (cliente)
    path('catalogo/', views.ver_catalogo, name="catalogo"),

    # módulo carrito
    path('carrito/', views.ver_carrito, name="carrito"),
    path('agregar_carrito/<int:id>/', views.agregar_carrito, name="agregar_carrito"),
    path('eliminar_carrito/<int:id>/', views.eliminar_carrito, name="eliminar_carrito"),
    path('actualizar_carrito/<int:id>/', views.actualizar_carrito, name="actualizar_carrito"),

    # módulo pedidos
    path('pedidos/', views.ver_pedidos, name="pedidos"),
    path('crear_pedido/', views.crear_pedido, name="crear_pedido"),
    path('actualizar_estado_pedido/<int:id>/', views.actualizar_estado_pedido, name="actualizar_estado_pedido"),
    path('detalle_pedido/<int:id>/', views.ver_detalle_pedido, name="detalle_pedido"),

    # módulo pagos
    path('pagos/', views.ver_pagos, name="pagos"),
    path('registrar_pago/<int:id>/', views.registrar_pago, name="registrar_pago"),

    # módulo compras
    path('compras/', views.ver_compras, name="compras"),
    path('crear_compra/', views.crear_compra, name="crear_compra"),
    path('detalle_compra/<int:id>/', views.ver_detalle_compra, name="detalle_compra"),
    path('agregar_detalle_compra/<int:id>/', views.agregar_detalle_compra, name="agregar_detalle_compra"),
    path('eliminar_detalle_compra/<int:id>/', views.eliminar_detalle_compra, name="eliminar_detalle_compra"),
    path('recibir_compra/<int:id>/', views.recibir_compra, name="recibir_compra"),

    # módulo movimientos inventario
    path('movimientos/', views.ver_movimientos, name="movimientos"),

    # módulo contabilidad
    path('contabilidad/', views.ver_contabilidad, name="contabilidad"),
]