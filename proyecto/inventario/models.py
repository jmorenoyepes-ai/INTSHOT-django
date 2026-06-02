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
    categoria = models.CharField(max_length=50)
    talla = models.CharField(max_length=10)
    stock = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.id} - {self.nombre} {self.talla} - Rol: {self.color}"
    
