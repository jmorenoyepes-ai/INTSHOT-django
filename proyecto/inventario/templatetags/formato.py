# Filtros propios para mostrar la información con formato

from django import template
from inventario.utilidades import formato_pesos

register = template.Library()

@register.filter
def pesos(valor):
    # Muestra un número como pesos colombianos. Ejemplo: 25000 -> $ 25.000
    return formato_pesos(valor)
