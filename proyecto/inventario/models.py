from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=254)
    telefono = models.CharField(max_length=20)
    ROLES = (
        ("Administrador", "ADMINISTRADOR"),
        ("Empleado", "EMPLEADO"),
        ("Cliente", "CLIENTE"),
    )

    rol = models.CharField(max_length=15, choices=ROLES, default = "Cliente")
    def __str__(self):
        return f"{self.id} - {self.nombre} {self.apellido}"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    color = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=254)
    talla = models.CharField(max_length=10)
    stock = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    CATEGORIAS = (
        ("Camisetas", "CAMISETAS"),
        ("Pantalones", "PANTALONES"),
        ("Chaquetas", "CHAQUETAS"),
        ("Accesorios", "ACCESORIOS"),
        ("Insumos", "INSUMOS"),
        ("Otros", "OTROS"),
    )

    categoria = models.CharField(max_length=50, choices=CATEGORIAS )


    def __str__(self):
        return f"{self.id} - {self.nombre} {self.talla} - Rol: {self.color}"
    
class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return f"{self.id} - {self.nombre} "
    
class Carrito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f"{self.usuario.nombre} - {self.producto.nombre}"

class Pedido(models.Model):
    usuario = models.ForeignKey(Usuario,on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    ESTADOS = (
        ("Pendiente", "PENDIENTE"),
        ("En proceso", "EN PROCESO"),
        ("Enviado", "ENVIADO"),
        ("Entregado", "ENTREGADO"),
        ("Cancelado", "CANCELADO"),
    )
    estado = models.CharField(max_length=20,choices=ESTADOS,default="Pendiente")

    def total(self):
        detalles = DetallePedido.objects.filter(pedido=self)
        return sum(d.subtotal() for d in detalles)

    def pagado(self):
        return Pago.objects.filter(pedido=self).exists()

    def __str__(self):
        return f"Pedido #{self.id}"
    
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido,on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10,decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre}"
    

class Pago(models.Model):
    pedido = models.ForeignKey(Pedido,on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10,decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    METODOS = (
        ("Efectivo", "EFECTIVO"),
        ("Tarjeta", "TARJETA"),
        ("Transferencia", "TRANSFERENCIA"),
    )
    metodo = models.CharField(max_length=20,choices=METODOS)

    def __str__(self):
        return f"Pago #{self.id}"
    
class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor,on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    ESTADOS = (
    ("Pendiente", "PENDIENTE"),
    ("Recibida", "RECIBIDA"),
    ("Recibida parcialmente", "RECIBIDA PARCIALMENTE"),
    )

    estado = models.CharField(max_length=30,choices=ESTADOS,default="Pendiente")

    def total(self):
        detalles = DetalleCompra.objects.filter(compra=self)
        return sum(d.subtotal() for d in detalles)

    def __str__(self):
        return f"Compra #{self.id}"
    
class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra,on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    cantidad_recibida = models.IntegerField(default=0)
    precio_unitario = models.DecimalField(max_digits=10,decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre}"

class MovimientoInventario(models.Model):
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=200)
    TIPOS = (
        ("Entrada", "ENTRADA"),
        ("Salida", "SALIDA"),
    )
    tipo = models.CharField(max_length=10,choices=TIPOS)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre}"


class MovimientoContable(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    TIPOS = (
        ("Ingreso", "INGRESO"),
        ("Egreso", "EGRESO"),
    )
    tipo = models.CharField(max_length=10, choices=TIPOS)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.CharField(max_length=300)
    
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True)
    compra = models.ForeignKey(Compra, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} ${self.valor} - {self.descripcion}"
