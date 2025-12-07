from django.core.validators import MinValueValidator
from django.db import models


class Tienda(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    cuenta = models.ForeignKey("users.Cuenta", on_delete=models.PROTECT, related_name="tiendas")

    class Meta:
        db_table = "tienda"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
    )
    esta_activa = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True)
    descripcion_prompt = models.TextField(blank=True, null=True)
    stock = models.IntegerField(default=0)
    agendable = models.BooleanField(default=True)

    class Meta:
        db_table = "producto"

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    esta_activa = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True)
    descripcion_prompt = models.TextField(blank=True, null=True)
    regla = models.ForeignKey("agents.Regla", on_delete=models.PROTECT, blank=True, null=True, related_name="categorias")
    logica_venta = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "categoria"

    def __str__(self):
        return self.nombre


class CategoriaTienda(models.Model):
    id = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, blank=True, null=True, related_name="tiendas")
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, blank=True, null=True, related_name="categorias")

    class Meta:
        db_table = "categoria_tienda"


class ProductoCategoria(models.Model):
    id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, blank=True, null=True, related_name="categoria_relaciones"
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, blank=True, null=True, related_name="producto_relaciones"
    )

    class Meta:
        db_table = "producto_categoria"


class Agenda(models.Model):
    id = models.AutoField(primary_key=True)
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    cliente_id = models.IntegerField(blank=True, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="agendas")

    class Meta:
        db_table = "agenda"

    def __str__(self):
        return f"Agenda {self.inicio} - {self.fin}"
