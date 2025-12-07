from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from commerce.models import CheckIn, Order
from sales.models import SaleEvent, SaleItem
from users.models import Cuenta
from ecommerce.models import Producto, Tienda
from scheduling.models import RecursoReservable, ReglaDisponibilidadRecurrente, Servicio


class CommerceFlowTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser("admin", "admin@example.com", "pass1234")
        self.client.force_authenticate(self.user)
        self.cuenta = Cuenta.objects.create(user=self.user, nombre="Cuenta Test", nombre_usuario="ctest", contrasena="x")
        self.tienda = Tienda.objects.create(nombre="Tienda Test", cuenta=self.cuenta)
        self.producto = Producto.objects.create(nombre="Producto Test", precio=Decimal("20.00"), stock=10, agendable=True)

    def test_carrito_checkout_pago(self):
        add_resp = self.client.post(
            "/api/commerce/cart/items/",
            {"tienda_id": self.tienda.id, "producto_id": self.producto.id, "quantity": 2},
            format="json",
        )
        self.assertEqual(add_resp.status_code, 201)

        checkout_resp = self.client.post(
            "/api/commerce/checkout/",
            {"tienda_id": self.tienda.id},
            format="json",
        )
        self.assertEqual(checkout_resp.status_code, 201)
        order_id = checkout_resp.data["id"]

        pay_resp = self.client.post(
            f"/api/commerce/orders/{order_id}/pay/",
            {"provider": "testpay", "external_id": "ext-1"},
            format="json",
        )
        self.assertEqual(pay_resp.status_code, 200)

        order = Order.objects.get(pk=order_id)
        self.assertEqual(order.status, Order.Status.PAGADA)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 8)

        self.assertTrue(SaleEvent.objects.filter(order_id=order_id).exists())
        self.assertEqual(SaleItem.objects.filter(sale_event__order_id=order_id).count(), 1)
        self.assertTrue(CheckIn.objects.filter(order_item__order_id=order_id).exists())

        # idempotencia: pagar dos veces no duplica
        self.client.post(
            f"/api/commerce/orders/{order_id}/pay/",
            {"provider": "testpay", "external_id": "ext-1"},
            format="json",
        )
        self.assertEqual(SaleEvent.objects.filter(order_id=order_id).count(), 1)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 8)

    def test_reserva_pagada_crea_venta_y_checkin(self):
        recurso = RecursoReservable.objects.create(nombre="Sala A", zona_horaria="UTC", capacidad=1)
        servicio = Servicio.objects.create(recurso=recurso, nombre="Consulta", duracion=timedelta(minutes=30))
        ahora = timezone.now()
        ReglaDisponibilidadRecurrente.objects.create(
            recurso=recurso,
            servicio=servicio,
            dia_semana=ahora.weekday(),
            hora_inicio="00:00:00",
            hora_fin="23:59:59",
        )
        inicio = ahora.replace(hour=10, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(minutes=40)
        cita_resp = self.client.post(
            reverse("citas-list"),
            {
                "recurso": recurso.id,
                "servicio": servicio.id,
                "producto": self.producto.id,
                "titulo": "Visita",
                "inicio": inicio.isoformat(),
                "fin": fin.isoformat(),
                "user": self.user.id,
            },
            format="json",
        )
        self.assertEqual(cita_resp.status_code, 201)
        cita_id = cita_resp.data["id"]

        patch_resp = self.client.patch(
            reverse("citas-detail", args=[cita_id]),
            {"pago_confirmado": True, "user": self.user.id},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, 200)

        sale = SaleEvent.objects.get(cita_id=cita_id)
        self.assertEqual(sale.source, SaleEvent.Source.RESERVATION)
        self.assertEqual(SaleItem.objects.filter(sale_event=sale).count(), 1)
        self.assertTrue(CheckIn.objects.filter(cita_id=cita_id, producto=self.producto).exists())

        # idempotencia: re-guardar no duplica
        self.client.patch(
            reverse("citas-detail", args=[cita_id]),
            {"pago_confirmado": True, "user": self.user.id},
            format="json",
        )
        self.assertEqual(SaleEvent.objects.filter(cita_id=cita_id).count(), 1)
        self.assertEqual(CheckIn.objects.filter(cita_id=cita_id).count(), 1)
