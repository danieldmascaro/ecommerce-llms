from decimal import Decimal
from typing import Tuple

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from sales.services import create_sale_from_order, guess_categoria_snapshot
from ecommerce.models import Producto, Tienda

from .models import Cart, CartItem, CheckIn, Order, OrderItem, Payment


def get_or_create_cart(user, tienda: Tienda) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user, tienda=tienda, status=Cart.Status.ABIERTO)
    return cart


def _categoria_snapshot(producto: Producto) -> Tuple[int | None, str]:
    return guess_categoria_snapshot(producto)


def add_item_to_cart(user, tienda: Tienda, producto: Producto, quantity: int) -> Cart:
    if not producto.esta_activa:
        raise ValidationError("El producto esta inactivo.")
    if quantity < 1:
        raise ValidationError("La cantidad debe ser mayor a 0.")

    cart = get_or_create_cart(user, tienda)
    cat_id, cat_nombre = _categoria_snapshot(producto)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        producto=producto,
        defaults={
            "cantidad": quantity,
            "precio_unitario": producto.precio or Decimal("0.00"),
            "categoria_snapshot_id": cat_id,
            "categoria_snapshot_nombre": cat_nombre or "",
        },
    )
    if not created:
        item.cantidad += quantity
        item.precio_unitario = item.precio_unitario or producto.precio or Decimal("0.00")
        item.categoria_snapshot_id = item.categoria_snapshot_id or cat_id
        item.categoria_snapshot_nombre = item.categoria_snapshot_nombre or (cat_nombre or "")
        item.save(update_fields=["cantidad", "precio_unitario", "categoria_snapshot_id", "categoria_snapshot_nombre"])
    return cart


def update_item_quantity(user, tienda: Tienda, producto: Producto, quantity: int) -> Cart:
    cart = get_or_create_cart(user, tienda)
    try:
        item = CartItem.objects.get(cart=cart, producto=producto)
    except CartItem.DoesNotExist:
        raise ValidationError("El producto no esta en el carrito.")

    if quantity < 1:
        item.delete()
        return cart

    item.cantidad = quantity
    item.save(update_fields=["cantidad", "updated_at"])
    return cart


def remove_item_from_cart(user, tienda: Tienda, producto: Producto) -> Cart:
    cart = get_or_create_cart(user, tienda)
    CartItem.objects.filter(cart=cart, producto=producto).delete()
    return cart


def cart_summary(cart: Cart) -> dict:
    items = cart.items.all()
    subtotal = sum((item.precio_unitario * item.cantidad for item in items), Decimal("0.00"))
    total_items = sum((item.cantidad for item in items), 0)
    return {
        "cart_id": cart.id,
        "tienda_id": cart.tienda_id,
        "status": cart.status,
        "subtotal": subtotal,
        "total_items": total_items,
        "items": [
            {
                "producto_id": item.producto_id,
                "producto_nombre": item.producto.nombre,
                "cantidad": item.cantidad,
                "precio_unitario": item.precio_unitario,
                "total_linea": item.total_linea,
            }
            for item in items
        ],
    }


@transaction.atomic
def checkout_cart(user, tienda: Tienda) -> Order:
    cart = get_or_create_cart(user, tienda)
    items = list(cart.items.select_related("producto"))
    if not items:
        raise ValidationError("El carrito esta vacio.")

    order = Order.objects.create(user=user, tienda=tienda, cart=cart, status=Order.Status.PENDIENTE)
    total_items = 0
    subtotal = Decimal("0.00")
    for item in items:
        cat_id = item.categoria_snapshot_id
        cat_nombre = item.categoria_snapshot_nombre
        if cat_id is None or not cat_nombre:
            cat_id, cat_nombre = _categoria_snapshot(item.producto)
        total_linea = item.precio_unitario * item.cantidad
        OrderItem.objects.create(
            order=order,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            total_linea=total_linea,
            categoria_snapshot_id=cat_id,
            categoria_snapshot_nombre=cat_nombre or "",
        )
        total_items += item.cantidad
        subtotal += total_linea

    order.total_items = total_items
    order.subtotal = subtotal
    order.total = subtotal
    order.save(update_fields=["total_items", "subtotal", "total", "updated_at"])

    cart.status = Cart.Status.FINALIZADO
    cart.save(update_fields=["status", "updated_at"])
    return order


@transaction.atomic
def confirm_payment(order: Order, provider: str, external_id: str | None = None, raw_response=None) -> Order:
    if order.status == Order.Status.PAGADA:
        return order

    payment_defaults = {
        "provider": provider,
        "amount": order.total,
        "status": Payment.Status.APROBADO,
        "raw_response": raw_response or {},
    }
    payment, created = Payment.objects.get_or_create(
        order=order, external_id=external_id, defaults=payment_defaults
    )
    if not created and payment.status != Payment.Status.APROBADO:
        payment.status = Payment.Status.APROBADO
        payment.raw_response = raw_response or payment.raw_response
        payment.provider = provider or payment.provider
        payment.amount = order.total
        payment.save(update_fields=["status", "raw_response", "provider", "amount"])

    for item in order.items.select_related("producto"):
        producto = item.producto
        if producto.stock is not None and producto.stock < item.cantidad:
            raise ValidationError(f"Stock insuficiente para {producto.nombre}.")
        producto.stock = (producto.stock or 0) - item.cantidad
        producto.save(update_fields=["stock"])

    order.status = Order.Status.PAGADA
    order.paid_at = timezone.now()
    order.save(update_fields=["status", "paid_at", "updated_at"])

    create_sale_from_order(order)
    _crear_checkins_para_order(order)
    return order


def _crear_checkins_para_order(order: Order) -> None:
    for item in order.items.select_related("producto"):
        producto = item.producto
        if not producto.agendable:
            continue
        CheckIn.objects.get_or_create(
            order_item=item,
            defaults={
                "producto": producto,
                "tienda": order.tienda,
                "user": order.user,
                "status": CheckIn.Status.PENDIENTE,
            },
        )
