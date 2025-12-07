from decimal import Decimal
from typing import Tuple

from django.db import transaction

from ecommerce.models import Categoria, Producto

from .models import SaleEvent, SaleItem


def guess_categoria_snapshot(producto: Producto) -> Tuple[int | None, str]:
    relacion = (
        producto.categoria_relaciones.select_related("categoria")
        .filter(categoria__esta_activa=True)
        .first()
    )
    if relacion and relacion.categoria:
        categoria: Categoria = relacion.categoria
        return categoria.id, categoria.nombre
    return None, ""


@transaction.atomic
def create_sale_from_order(order) -> SaleEvent:
    sale, created = SaleEvent.objects.get_or_create(
        order=order,
        defaults={
            "user": order.user,
            "tienda": order.tienda,
            "source": SaleEvent.Source.CART_CHECKOUT,
        },
    )
    if not created:
        return sale

    total_amount = Decimal("0.00")
    total_items = 0
    for item in order.items.select_related("producto"):
        cat_id, cat_nombre = guess_categoria_snapshot(item.producto)
        SaleItem.objects.create(
            sale_event=sale,
            producto=item.producto,
            producto_nombre=item.producto.nombre,
            categoria_snapshot_id=item.categoria_snapshot_id or cat_id,
            categoria_snapshot_nombre=item.categoria_snapshot_nombre or (cat_nombre or ""),
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            total_linea=item.total_linea,
        )
        total_amount += item.total_linea
        total_items += item.cantidad

    sale.total_amount = total_amount
    sale.total_items = total_items
    sale.save(update_fields=["total_amount", "total_items"])
    return sale


@transaction.atomic
def create_sale_from_cita(cita) -> SaleEvent:
    if not cita.producto:
        raise ValueError("La cita no tiene producto asociado.")

    sale, created = SaleEvent.objects.get_or_create(
        cita=cita,
        defaults={
            "user": getattr(cita, "user", None),
            "source": SaleEvent.Source.RESERVATION,
            "tienda": guess_tienda_from_producto(cita.producto),
        },
    )
    if not created:
        return sale

    producto = cita.producto
    cat_id, cat_nombre = guess_categoria_snapshot(producto)
    precio = producto.precio or Decimal("0.00")
    SaleItem.objects.create(
        sale_event=sale,
        producto=producto,
        producto_nombre=producto.nombre,
        categoria_snapshot_id=cat_id,
        categoria_snapshot_nombre=cat_nombre or "",
        cantidad=1,
        precio_unitario=precio,
        total_linea=precio,
    )
    sale.total_items = 1
    sale.total_amount = precio
    sale.save(update_fields=["total_items", "total_amount"])
    return sale


def guess_tienda_from_producto(producto: Producto):
    relacion = (
        producto.categoria_relaciones.select_related("categoria")
        .filter(categoria__tiendas__isnull=False)
        .first()
    )
    if relacion and relacion.categoria:
        categoria = relacion.categoria
        tienda_rel = categoria.tiendas.select_related("tienda").first()
        if tienda_rel:
            return tienda_rel.tienda
    return None
