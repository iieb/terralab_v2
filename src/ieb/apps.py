from django.apps import AppConfig


class IebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ieb'

    def ready(self):
        import ieb.signals  # noqa: F401
