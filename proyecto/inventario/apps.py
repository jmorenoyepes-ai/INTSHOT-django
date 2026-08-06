from django.apps import AppConfig


class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'

    def ready(self):
            import inventario.signals  # <--- Carga el archivo de señales

"""class TuAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tu_app_de_servicios'

    def ready(self):
        import tu_app_de_servicios.signals  # <--- Carga el archivo de señales"""