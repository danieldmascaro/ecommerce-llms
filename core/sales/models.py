from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from ecommerce.models import Producto, Tienda


class SaleEvent(models.Model):
    class Source(models.TextChoices):
        CART_CHECKOUT = "CART_CHECKOUT", "checkout_carrito"
        RESERVATION = "RESERVATION", "reserva"
        MANUAL = "MANUAL", "manual"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name="sale_events", null=True, blank=True)
    source = models.CharField(max_length=20, choices=Source.choices)
    order = models.ForeignKey(
        "commerce.Order", on_delete=models.PROTECT, related_name="sale_events", null=True, blank=True
    )
    cita = models.ForeignKey(
        "scheduling.Cita", on_delete=models.PROTECT, related_name="sale_events", null=True, blank=True
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0"))]
    )
    total_items = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sales_event"
        indexes = [
            models.Index(fields=["source"]),
            models.Index(fields=["tienda"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["order"], name="uq_sale_por_order", condition=models.Q(order__isnull=False)),
            models.UniqueConstraint(fields=["cita"], name="uq_sale_por_cita", condition=models.Q(cita__isnull=False)),
        ]

    def __str__(self):
        return f"SaleEvent #{self.pk} {self.source}"


class SaleItem(models.Model):
    sale_event = models.ForeignKey(SaleEvent, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="sale_items")
    producto_nombre = models.CharField(max_length=255)
    categoria_snapshot_id = models.IntegerField(null=True, blank=True)
    categoria_snapshot_nombre = models.CharField(max_length=255, blank=True)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    total_linea = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        db_table = "sales_item"
        indexes = [
            models.Index(fields=["sale_event"]),
            models.Index(fields=["producto"]),
        ]

    def __str__(self):
        return f"{self.producto_nombre} x{self.cantidad}"
