from django.apps import AppConfig


class SchedulingConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "scheduling"

    def ready(self):
        # Import signals para conectar hooks de cita pagada.
        from . import signals  # noqa: F401
