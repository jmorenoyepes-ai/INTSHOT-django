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
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.nombre} {self.talla} - Color: {self.color}"
    
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
    usuario = models.ForeignKey(Usuario,on_delete=models.PROTECT)
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
    proveedor = models.ForeignKey(Proveedor,on_delete=models.PROTECT)
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
    producto = models.ForeignKey(Producto,on_delete=models.PROTECT)
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


# Configuración de la página de inicio (landing)

class Configuracion(models.Model):
    # Datos generales del sitio
    nombre_empresa = models.CharField(max_length=100, default="INTSHOT")
    logo = models.ImageField(upload_to='configuracion/', null=True, blank=True)

    # Sección principal (hero)
    hero_titulo = models.CharField(max_length=200, default="Optimiza la gestión de tu inventario y pedidos con INTSHOT")
    hero_texto = models.CharField(max_length=500, default="Un sistema diseñado especialmente para empresas textiles que buscan controlar insumos, productos terminados y pedidos de manera eficiente.")
    hero_imagen = models.ImageField(upload_to='configuracion/', null=True, blank=True)

    # Títulos de las demás secciones
    titulo_catalogo = models.CharField(max_length=100, default="Nuestro catálogo")
    titulo_caracteristicas = models.CharField(max_length=100, default="Características")
    titulo_beneficios = models.CharField(max_length=100, default="¿Por qué elegir INTSHOT?")

    # Pie de página y datos de contacto
    texto_footer = models.CharField(max_length=300, default="Todos los derechos reservados", blank=True)
    telefono = models.CharField(max_length=20, default="", blank=True)
    correo = models.EmailField(max_length=254, default="", blank=True)
    direccion = models.CharField(max_length=200, default="", blank=True)

    def __str__(self):
        return f"Configuración de {self.nombre_empresa}"


class Vineta(models.Model):
    # Cada punto de la lista que aparece en la sección principal
    texto = models.CharField(max_length=200)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return self.texto


class Caracteristica(models.Model):
    # Cada tarjeta de la sección "Características"
    titulo = models.CharField(max_length=100)
    texto = models.CharField(max_length=300)
    imagen = models.ImageField(upload_to='configuracion/', null=True, blank=True)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return self.titulo


class Beneficio(models.Model):
    # Cada punto de la sección "¿Por qué elegir INTSHOT?"
    icono = models.CharField(max_length=10, default="", blank=True)
    titulo = models.CharField(max_length=100)
    texto = models.CharField(max_length=300)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return self.titulo


def obtener_configuracion():
    # Devuelve la configuración del sitio.
    # La primera vez que se usa, la crea junto con el contenido inicial de la página.
    q = Configuracion.objects.first()

    if not q:
        q = Configuracion.objects.create(
            logo="configuracion/Logo-blanco.jpeg",
            hero_imagen="configuracion/INTSHOT.jpg",
        )

        Vineta.objects.create(texto="Registra clientes y pedidos fácilmente.", orden=1)
        Vineta.objects.create(texto="Supervisa tu inventario de materiales y prendas.", orden=2)
        Vineta.objects.create(texto="Accede a tus datos desde cualquier dispositivo.", orden=3)

        Caracteristica.objects.create(
            titulo="Inventario",
            texto="Control total de productos e insumos con actualizaciones en tiempo real.",
            imagen="configuracion/inventario.jpg",
            orden=1
        )
        Caracteristica.objects.create(
            titulo="Pedidos y Clientes",
            texto="Registra, edita y consulta fácilmente los pedidos realizados por tus clientes.",
            imagen="configuracion/Clientes.avif",
            orden=2
        )
        Caracteristica.objects.create(
            titulo="Reportes y Control",
            texto="Genera reportes detallados para mejorar la toma de decisiones y el control interno.",
            imagen="configuracion/Reportes.png",
            orden=3
        )

        Beneficio.objects.create(icono="🚀", titulo="Rápido", texto="y con una interfaz moderna e intuitiva.", orden=1)
        Beneficio.objects.create(icono="🔒", titulo="Seguro", texto="protege los datos de tu empresa.", orden=2)
        Beneficio.objects.create(icono="🧵", titulo="Ideal", texto="para talleres y empresas textiles.", orden=3)

    return q
