from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0010_detallecompra_cantidad_recibida_alter_compra_estado_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='productos/'),
        ),
    ]
