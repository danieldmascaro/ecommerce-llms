from django.db import models

from ecommerce.models import Categoria, Producto, Tienda


class Reglamento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = "reglamento"

    def __str__(self):
        return self.nombre


class Regla(models.Model):
    id = models.AutoField(primary_key=True)
    reglamento = models.ForeignKey(Reglamento, on_delete=models.PROTECT, related_name="reglas")
    orden = models.IntegerField()
    texto = models.TextField()
    esta_seleccionable = models.BooleanField(default=True)

    class Meta:
        db_table = "regla"
        ordering = ["orden"]

    def __str__(self):
        return f"Regla {self.orden} - {self.reglamento}"


class ModeloIA(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = "modelo_ia"

    def __str__(self):
        return self.nombre


class TipoAgente(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "tipo_agente"

    def __str__(self):
        return self.nombre


class FlujoAgente(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    nombre_comercial = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name="flujos_agente")

    class Meta:
        db_table = "flujo_agente"

    def __str__(self):
        return self.nombre


class ProductoFlujoAgente(models.Model):
    id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, blank=True, null=True, related_name="flujo_agente_relaciones"
    )
    flujo_agente = models.ForeignKey(
        FlujoAgente, on_delete=models.PROTECT, blank=True, null=True, related_name="producto_relaciones"
    )

    class Meta:
        db_table = "producto_flujo_agente"


class CategoriaFlujoAgente(models.Model):
    id = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, blank=True, null=True, related_name="flujos_agente"
    )
    flujo_agente = models.ForeignKey(
        FlujoAgente, on_delete=models.PROTECT, blank=True, null=True, related_name="categorias"
    )

    class Meta:
        db_table = "categoria_flujo_agente"


class Agente(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name="agentes")
    flujo_agente = models.ForeignKey(FlujoAgente, on_delete=models.PROTECT, related_name="agentes")
    tipo_agente = models.ForeignKey(TipoAgente, on_delete=models.PROTECT, related_name="agentes")
    modelo_ia = models.ForeignKey(ModeloIA, on_delete=models.PROTECT, related_name="agentes")
    reglamento = models.ForeignKey(
        Reglamento, on_delete=models.PROTECT, blank=True, null=True, related_name="agentes"
    )
    logica = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "agente"

    def __str__(self):
        return self.nombre


class AgentSession(models.Model):
    session_id = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "agent_sessions"

    def __str__(self):
        return self.session_id


class AgentMessage(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(AgentSession, to_field="session_id", on_delete=models.PROTECT, related_name="messages")
    message_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "agent_messages"

    def __str__(self):
        return f"Message {self.id}"
