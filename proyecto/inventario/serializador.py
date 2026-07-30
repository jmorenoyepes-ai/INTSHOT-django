# importamos los modelos de la base de datos 
from .models import *

# importamos la libreria
from rest_framework import serializers

# Creamos una clase tipo serializador, para mapear nuestro modelo
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'correo', 'telefono', 'rol']
        # fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        # fields = ['id', 'nombre', 'color', 'descripcion', 'talla', 'stock', 'precio', 'categoria', 'imagen']
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        # fields = ['id', 'nombre', 'telefono', 'correo']
        fields = '__all__'

class CarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrito
        # fields = ['id', 'usuario', 'producto', 'cantidad', 'fecha_agregado']
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        # fields = ['id', 'usuario', 'fecha', 'estado']
        fields = '__all__'

class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        # fields = ['id', 'pedido', 'producto', 'cantidad', 'precio_unitario']
        fields = '__all__'

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        # fields = ['id', 'pedido', 'valor', 'fecha', 'metodo']
        fields = '__all__'

class CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compra
        # fields = ['id', 'proveedor', 'fecha', 'estado']
        fields = '__all__'

class DetalleCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCompra
        # fields = ['id', 'compra', 'producto', 'cantidad', 'cantidad_recibida', 'precio_unitario']
        fields = '__all__'

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoInventario
        # fields = ['id', 'producto', 'cantidad', 'fecha', 'descripcion', 'tipo']
        fields = '__all__'

class MovimientoContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoContable
        # fields = ['id', 'fecha', 'tipo', 'valor', 'descripcion', 'pedido', 'compra']
        fields = '__all__'
