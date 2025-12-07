from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from ecommerce.models import Producto, Tienda


class Cart(models.Model):
    class Status(models.TextChoices):
        ABIERTO = "open", "abierto"
        FINALIZADO = "closed", "finalizado"
        ABANDONADO = "abandoned", "abandonado"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts")
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name="carts")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ABIERTO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "commerce_cart"
        indexes = [
            models.Index(fields=["user", "tienda"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tienda"],
                condition=Q(status="open"),
                name="uq_cart_abierto_usuario_tienda",
            ),
        ]

    def __str__(self):
        return f"Cart #{self.pk} ({self.user})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="cart_items")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    categoria_snapshot_id = models.IntegerField(null=True, blank=True)
    categoria_snapshot_nombre = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "commerce_cart_item"
        constraints = [
            models.UniqueConstraint(fields=["cart", "producto"], name="uq_item_unico_por_producto"),
        ]

    @property
    def total_linea(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.producto} x{self.cantidad}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDIENTE = "pending", "pendiente"
        PAGADA = "paid", "pagada"
        CANCELADA = "cancelled", "cancelada"
        REEMBOLSADA = "refunded", "reembolsada"

    cart = models.ForeignKey(Cart, on_delete=models.PROTECT, related_name="orders", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDIENTE)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_items = models.PositiveIntegerField(default=0)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "commerce_order"
        indexes = [
            models.Index(fields=["user", "tienda"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="order_items")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    total_linea = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    categoria_snapshot_id = models.IntegerField(null=True, blank=True)
    categoria_snapshot_nombre = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "commerce_order_item"
        indexes = [
            models.Index(fields=["order", "producto"]),
        ]

    def __str__(self):
        return f"{self.producto} ({self.cantidad})"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDIENTE = "pending", "pendiente"
        APROBADO = "succeeded", "aprobado"
        FALLIDO = "failed", "fallido"

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payments")
    provider = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDIENTE)
    external_id = models.CharField(max_length=255, blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "commerce_payment"
        indexes = [
            models.Index(fields=["order", "status"]),
        ]

    def __str__(self):
        return f"Payment {self.provider} #{self.pk}"


class CheckIn(models.Model):
    class Status(models.TextChoices):
        PENDIENTE = "pending", "pendiente"
        COMPLETADO = "done", "completado"

    order_item = models.ForeignKey(
        OrderItem, on_delete=models.SET_NULL, related_name="checkins", null=True, blank=True
    )
    cita = models.ForeignKey(
        "scheduling.Cita", on_delete=models.SET_NULL, related_name="checkins", null=True, blank=True
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="checkins")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name="checkins", null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDIENTE)
    done_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "commerce_checkin"
        indexes = [
            models.Index(fields=["tienda", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["order_item"], condition=Q(order_item__isnull=False), name="uq_checkin_por_order_item"
            ),
            models.UniqueConstraint(
                fields=["cita", "producto"],
                condition=Q(cita__isnull=False),
                name="uq_checkin_por_cita_producto",
            ),
        ]

    def __str__(self):
        return f"CheckIn {self.producto} ({self.get_status_display()})"
