from django.conf import settings
from django.db import models
from django.utils import timezone


class Cuenta(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cuenta")
    nombre = models.CharField(max_length=255)
    nombre_usuario = models.CharField(max_length=255, unique=True)
    contrasena = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "cuenta"

    def __str__(self):
        return self.nombre
