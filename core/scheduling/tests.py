from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase


class SchedulingApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser("admin", "admin@example.com", "pass1234")
        self.client.force_authenticate(self.user)

    def _post(self, name: str, data: dict):
        url = reverse(name)
        return self.client.post(url, data, format="json")

    def _crear_producto(self):
        resp = self._post("productos-list", {"nombre": "Producto X", "precio": "12.50"})
        self.assertEqual(resp.status_code, 201)
        return resp.data["id"]

    def test_programacion_crud_completo(self):
        producto_id = self._crear_producto()
        # Recurso
        recurso_resp = self._post(
            "recursos-list",
            {"nombre": "Sala A", "zona_horaria": "UTC", "capacidad": 1},
        )
        self.assertEqual(recurso_resp.status_code, 201)
        recurso_id = recurso_resp.data["id"]

        # Servicio
        servicio_resp = self._post(
            "servicios-list",
            {
                "recurso": recurso_id,
                "nombre": "Consulta",
                "duracion": "00:30:00",
                "buffer_antes": "00:05:00",
                "buffer_despues": "00:05:00",
            },
        )
        self.assertEqual(servicio_resp.status_code, 201)
        servicio_id = servicio_resp.data["id"]

        # Regla de disponibilidad
        ahora = timezone.now()
        regla_resp = self._post(
            "reglas-disponibilidad-list",
            {
                "recurso": recurso_id,
                "servicio": servicio_id,
                "dia_semana": ahora.weekday(),
                "hora_inicio": "09:00:00",
                "hora_fin": "18:00:00",
            },
        )
        self.assertEqual(regla_resp.status_code, 201)

        # Excepcion (apertura)
        fecha = ahora.date().isoformat()
        excepcion_resp = self._post(
            "excepciones-disponibilidad-list",
            {
                "recurso": recurso_id,
                "servicio": servicio_id,
                "fecha": fecha,
                "hora_inicio": "08:00:00",
                "hora_fin": "20:00:00",
                "tipo": "open",
                "motivo": "Horario extendido",
            },
        )
        self.assertEqual(excepcion_resp.status_code, 201)

        # Cita
        inicio = ahora.replace(hour=10, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(minutes=40)
        cita_resp = self._post(
            "citas-list",
            {
                "recurso": recurso_id,
                "servicio": servicio_id,
                "producto": producto_id,
                "titulo": "Visita Cliente",
                "inicio": inicio.isoformat(),
                "fin": fin.isoformat(),
                "notas": "Traer contrato",
            },
        )
        self.assertEqual(cita_resp.status_code, 201)
        cita_id = cita_resp.data["id"]

        # validar-espacio
        validar_resp = self._post(
            "citas-validar-espacio",
            {
                "recurso": recurso_id,
                "servicio": servicio_id,
                "inicio": (inicio + timedelta(hours=1)).isoformat(),
                "fin": (fin + timedelta(hours=1)).isoformat(),
            },
        )
        self.assertEqual(validar_resp.status_code, 200)

        # cancelar
        cancelar_resp = self.client.post(reverse("citas-cancelar", args=[cita_id]))
        self.assertEqual(cancelar_resp.status_code, 200)

        # actualizar servicio
        patch_resp = self.client.patch(
            reverse("servicios-detail", args=[servicio_id]),
            {"descripcion": "Actualizado"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, 200)

        # list endpoints
        self.assertEqual(self.client.get(reverse("recursos-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("servicios-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("reglas-disponibilidad-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("excepciones-disponibilidad-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("citas-list")).status_code, 200)

        # delete
        self.assertEqual(self.client.delete(reverse("citas-detail", args=[cita_id])).status_code, 204)
        self.assertEqual(self.client.delete(reverse("excepciones-disponibilidad-detail", args=[excepcion_resp.data["id"]])).status_code, 204)
        self.assertEqual(self.client.delete(reverse("reglas-disponibilidad-detail", args=[regla_resp.data["id"]])).status_code, 204)
        self.assertEqual(self.client.delete(reverse("servicios-detail", args=[servicio_id])).status_code, 204)
        self.assertEqual(self.client.delete(reverse("recursos-detail", args=[recurso_id])).status_code, 204)
