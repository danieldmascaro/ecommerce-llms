from django.contrib import admin

from .models import Cita, ExcepcionDisponibilidad, ReglaDisponibilidadRecurrente, RecursoReservable, Servicio


@admin.register(RecursoReservable)
class RecursoReservableAdmin(admin.ModelAdmin):
    list_display = ("nombre", "zona_horaria", "capacidad", "esta_activo", "creado_en")
    search_fields = ("nombre",)
    list_filter = ("esta_activo",)


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "recurso", "duracion", "esta_activo")
    list_filter = ("esta_activo", "recurso")
    search_fields = ("nombre", "recurso__nombre")


@admin.register(ReglaDisponibilidadRecurrente)
class ReglaDisponibilidadAdmin(admin.ModelAdmin):
    list_display = ("recurso", "servicio", "dia_semana", "hora_inicio", "hora_fin", "esta_activa")
    list_filter = ("dia_semana", "esta_activa", "recurso")


@admin.register(ExcepcionDisponibilidad)
class ExcepcionDisponibilidadAdmin(admin.ModelAdmin):
    list_display = ("recurso", "servicio", "fecha", "hora_inicio", "hora_fin", "tipo", "esta_activa")
    list_filter = ("tipo", "esta_activa", "fecha", "recurso")


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "recurso", "servicio", "producto", "user", "inicio", "fin", "estado", "pago_confirmado")
    list_filter = ("estado", "pago_confirmado", "recurso", "servicio")
    search_fields = ("titulo", "producto__nombre", "user__username")

