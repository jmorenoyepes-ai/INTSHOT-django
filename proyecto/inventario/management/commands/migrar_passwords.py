# Encripta las contraseñas que todavía están guardadas en texto plano.
# Uso: python manage.py migrar_passwords

from django.core.management.base import BaseCommand

from inventario.models import Usuario
from inventario.utilidades import password_en_texto_plano, guardar_password


class Command(BaseCommand):
    help = "Encripta (hashea) las contraseñas de los usuarios que están en texto plano"

    def handle(self, *args, **options):
        actualizados = 0

        for usuario in Usuario.objects.all():
            if password_en_texto_plano(usuario):
                guardar_password(usuario, usuario.password)
                usuario.save(update_fields=["password"])
                actualizados += 1

        if actualizados:
            self.stdout.write(self.style.SUCCESS(f"{actualizados} contraseña(s) encriptada(s) correctamente"))
        else:
            self.stdout.write(self.style.SUCCESS("No había contraseñas en texto plano"))
