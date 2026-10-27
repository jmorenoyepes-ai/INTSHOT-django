from django.db import migrations, models


CORREO_ANTERIOR = "intshotadmin@gmail.com"
CORREO_SUPER_ADMIN = "intshot1@gmail.com"


def marcar_super_admin(apps, schema_editor):
    # Corrige el correo de la cuenta de INTSHOT y la marca como super admin
    Usuario = apps.get_model("inventario", "Usuario")
    cuenta = (
        Usuario.objects.filter(correo=CORREO_SUPER_ADMIN).first()
        or Usuario.objects.filter(correo=CORREO_ANTERIOR).first()
    )
    if cuenta:
        cuenta.correo = CORREO_SUPER_ADMIN
        cuenta.rol = "Administrador"
        cuenta.es_super_admin = True
        cuenta.save()


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0017_tokenrecuperacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='es_super_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(marcar_super_admin, migrations.RunPython.noop),
    ]
