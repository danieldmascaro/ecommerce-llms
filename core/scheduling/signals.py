from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from commerce.models import CheckIn
from sales.services import create_sale_from_cita, guess_tienda_from_producto

from .models import Cita


@receiver(pre_save, sender=Cita)
def set_confirmed_at(sender, instance: Cita, **kwargs):
    if instance.pago_confirmado and not instance.confirmed_at:
        instance.confirmed_at = timezone.now()


@receiver(post_save, sender=Cita)
def on_cita_pagada(sender, instance: Cita, **kwargs):
    if not instance.pago_confirmado or not instance.producto:
        return

    create_sale_from_cita(instance)

    tienda = guess_tienda_from_producto(instance.producto)
    CheckIn.objects.get_or_create(
        cita=instance,
        producto=instance.producto,
        defaults={
            "tienda": tienda,
            "user": getattr(instance, "user", None),
            "status": CheckIn.Status.PENDIENTE,
        },
    )

