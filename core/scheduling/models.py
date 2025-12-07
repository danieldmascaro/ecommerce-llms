from datetime import timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from ecommerce.models import Producto


class RecursoReservable(models.Model):
    """Recurso reservable: salon, sala, especialista, etc."""

    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True)
    zona_horaria = models.CharField(max_length=64, default="UTC")
    capacidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    esta_activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "programacion_recurso"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["esta_activo"]),
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        errors = {}
        try:
            ZoneInfo(self.zona_horaria)
        except Exception:
            errors["zona_horaria"] = "Zona horaria no valida."
        if errors:
            raise ValidationError(errors)


class Servicio(models.Model):
    """Servicio asociado a un recurso (ej. consulta, demo, clase)."""

    recurso = models.ForeignKey(
        RecursoReservable,
        on_delete=models.PROTECT,
        related_name="servicios",
    )
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    duracion = models.DurationField(
        help_text="Duracion neta del servicio.",
        validators=[MinValueValidator(timedelta(seconds=1))],
    )
    buffer_antes = models.DurationField(default=timedelta(), validators=[MinValueValidator(timedelta())])
    buffer_despues = models.DurationField(default=timedelta(), validators=[MinValueValidator(timedelta())])
    esta_activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "programacion_servicio"
        constraints = [
            models.UniqueConstraint(fields=["recurso", "nombre"], name="uq_servicio_por_recurso"),
        ]
        indexes = [
            models.Index(fields=["recurso", "esta_activo"]),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.recurso})"

    @property
    def duracion_total_esperada(self) -> timedelta:
        return self.duracion + self.buffer_antes + self.buffer_despues


class ReglaDisponibilidadRecurrente(models.Model):
    """Regla recurrente semanal de disponibilidad."""

    class DiaSemana(models.IntegerChoices):
        LUNES = 0, "lunes"
        MARTES = 1, "martes"
        MIERCOLES = 2, "miercoles"
        JUEVES = 3, "jueves"
        VIERNES = 4, "viernes"
        SABADO = 5, "sabado"
        DOMINGO = 6, "domingo"

    recurso = models.ForeignKey(
        RecursoReservable,
        on_delete=models.CASCADE,
        related_name="reglas_disponibilidad",
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name="reglas_disponibilidad",
        blank=True,
        null=True,
        help_text="Opcional: regla especifica para un servicio del recurso.",
    )
    dia_semana = models.PositiveSmallIntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    vigente_desde = models.DateField(blank=True, null=True)
    vigente_hasta = models.DateField(blank=True, null=True)
    esta_activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "programacion_regla_disponibilidad"
        ordering = ["recurso", "dia_semana", "hora_inicio"]
        indexes = [
            models.Index(fields=["recurso", "dia_semana", "esta_activa"]),
        ]
        constraints = [
            models.CheckConstraint(check=Q(hora_fin__gt=F("hora_inicio")), name="chk_regla_fin_despues_inicio"),
            models.CheckConstraint(
                check=Q(vigente_hasta__gte=F("vigente_desde"))
                | Q(vigente_hasta__isnull=True)
                | Q(vigente_desde__isnull=True),
                name="chk_regla_rango_fechas",
            ),
        ]

    def clean(self):
        errors = {}
        if self.servicio and self.servicio.recurso_id != self.recurso_id:
            errors["servicio"] = "El servicio debe pertenecer al mismo recurso de la regla."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin} ({self.recurso})"


class ExcepcionDisponibilidad(models.Model):
    """Excepciones puntuales (cierres o aperturas extraordinarias)."""

    class Tipo(models.TextChoices):
        CERRADO = "closed", "cerrado"
        ABIERTO = "open", "abierto"

    recurso = models.ForeignKey(
        RecursoReservable,
        on_delete=models.CASCADE,
        related_name="excepciones_disponibilidad",
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name="excepciones_disponibilidad",
        blank=True,
        null=True,
        help_text="Opcional: excepcion especifica para un servicio del recurso.",
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo = models.CharField(max_length=8, choices=Tipo.choices)
    motivo = models.CharField(max_length=255, blank=True)
    esta_activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "programacion_excepcion_disponibilidad"
        ordering = ["-fecha", "hora_inicio"]
        indexes = [
            models.Index(fields=["recurso", "fecha"]),
            models.Index(fields=["recurso", "fecha", "tipo"]),
        ]
        constraints = [
            models.CheckConstraint(check=Q(hora_fin__gt=F("hora_inicio")), name="chk_excepcion_fin_despues_inicio"),
        ]

    def clean(self):
        errors = {}
        if self.servicio and self.servicio.recurso_id != self.recurso_id:
            errors["servicio"] = "El servicio debe pertenecer al mismo recurso de la excepcion."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.get_tipo_display()} {self.fecha} {self.hora_inicio}-{self.hora_fin} ({self.recurso})"


class Cita(models.Model):
    """Cita/reserva confirmada."""

    class Estado(models.TextChoices):
        AGENDADA = "scheduled", "agendada"
        CANCELADA = "cancelled", "cancelada"

    recurso = models.ForeignKey(
        RecursoReservable,
        on_delete=models.PROTECT,
        related_name="citas",
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name="citas",
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="citas",
        null=True,
        blank=True,
        help_text="Producto asociado a la cita (opcional).",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="citas",
        null=True,
        blank=True,
        help_text="Usuario comprador/cliente asociado.",
    )
    titulo = models.CharField(max_length=255, help_text="Referencia del evento/cliente.")
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.AGENDADA)
    pago_confirmado = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "programacion_cita"
        ordering = ["-inicio"]
        indexes = [
            models.Index(fields=["recurso", "inicio"]),
            models.Index(fields=["recurso", "estado"]),
            models.Index(fields=["producto", "inicio"]),
            models.Index(fields=["pago_confirmado"]),
        ]
        constraints = [
            models.CheckConstraint(check=Q(fin__gt=F("inicio")), name="chk_cita_fin_despues_inicio"),
        ]

    def clean(self):
        errors = {}

        if self.servicio and self.recurso and self.servicio.recurso_id != self.recurso_id:
            errors["servicio"] = "El servicio no pertenece al recurso seleccionado."
        if self.recurso and not self.recurso.esta_activo:
            errors["recurso"] = "El recurso esta inactivo."
        if self.servicio and not self.servicio.esta_activo:
            errors["servicio"] = "El servicio esta inactivo."
        if self.producto and not self.producto.esta_activa:
            errors["producto"] = "El producto esta inactivo."

        if self.inicio and self.fin:
            if self.fin <= self.inicio:
                errors["fin"] = "La hora de fin debe ser posterior a la de inicio."
            if timezone.is_naive(self.inicio) or timezone.is_naive(self.fin):
                errors["inicio"] = "Las fechas deben ser timezone-aware (USE_TZ activo)."
            if self._cruza_dia():
                errors["fin"] = "La cita debe iniciar y terminar el mismo dia para validar la disponibilidad."
            if not errors:
                self._validar_duracion_minima(errors)
                self._validar_solapes(errors)
                self._validar_disponibilidad(errors)

        if errors:
            raise ValidationError(errors)

    def _validar_duracion_minima(self, errors: dict) -> None:
        esperado = self.servicio.duracion_total_esperada if self.servicio else timedelta()
        duracion = self.fin - self.inicio
        if esperado and duracion < esperado:
            errors["fin"] = (
                f"La duracion minima para el servicio es {esperado}; "
                f"la cita dura {duracion}."
            )

    def _validar_solapes(self, errors: dict) -> None:
        qs = (
            Cita.objects.filter(recurso=self.recurso, estado=self.Estado.AGENDADA)
            .filter(inicio__lt=self.fin, fin__gt=self.inicio)
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        cantidad_solapada = qs.count()

        if cantidad_solapada >= self.recurso.capacidad:
            errors["inicio"] = "El recurso ya esta ocupado en ese intervalo."

    def _validar_disponibilidad(self, errors: dict) -> None:
        inicio_local, fin_local = self._fechas_locales()
        fecha = inicio_local.date()
        hora_inicio = inicio_local.time()
        hora_fin = fin_local.time()
        dia_semana = inicio_local.weekday()

        hay_cierre = ExcepcionDisponibilidad.objects.filter(
            recurso=self.recurso,
            tipo=ExcepcionDisponibilidad.Tipo.CERRADO,
            esta_activa=True,
            fecha=fecha,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio,
        ).filter(Q(servicio__isnull=True) | Q(servicio=self.servicio)).exists()

        if hay_cierre:
            errors["inicio"] = "Hay una excepcion de cierre en el horario solicitado."
            return

        hay_apertura = ExcepcionDisponibilidad.objects.filter(
            recurso=self.recurso,
            tipo=ExcepcionDisponibilidad.Tipo.ABIERTO,
            esta_activa=True,
            fecha=fecha,
            hora_inicio__lte=hora_inicio,
            hora_fin__gte=hora_fin,
        ).filter(Q(servicio__isnull=True) | Q(servicio=self.servicio)).exists()

        reglas = ReglaDisponibilidadRecurrente.objects.filter(
            recurso=self.recurso,
            dia_semana=dia_semana,
            esta_activa=True,
        ).filter(Q(servicio__isnull=True) | Q(servicio=self.servicio))

        reglas = reglas.filter(
            Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=fecha),
            Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=fecha),
        )

        regla_cubre = any(
            regla.hora_inicio <= hora_inicio <= regla.hora_fin and regla.hora_fin >= hora_fin
            for regla in reglas
        )

        if not (hay_apertura or regla_cubre):
            errors["inicio"] = "El intervalo solicitado esta fuera de la disponibilidad del recurso."

    def _fechas_locales(self):
        tz = ZoneInfo(self.recurso.zona_horaria or settings.TIME_ZONE)
        return timezone.localtime(self.inicio, tz), timezone.localtime(self.fin, tz)

    def _cruza_dia(self) -> bool:
        if not self.inicio or not self.fin:
            return False
        inicio_local, fin_local = self._fechas_locales()
        return inicio_local.date() != fin_local.date()

    def __str__(self):
        return f"{self.titulo} | {self.inicio} - {self.fin}"
