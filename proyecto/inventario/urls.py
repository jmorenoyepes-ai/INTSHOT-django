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

]
