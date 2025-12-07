from rest_framework import serializers

from .models import (
    Cita,
    ExcepcionDisponibilidad,
    ReglaDisponibilidadRecurrente,
    RecursoReservable,
    Servicio,
)


class RecursoReservableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecursoReservable
        fields = "__all__"


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instancia = self.instance or Servicio()
        for clave, valor in attrs.items():
            setattr(instancia, clave, valor)
        instancia.full_clean()
        return attrs


class ReglaDisponibilidadRecurrenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReglaDisponibilidadRecurrente
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instancia = self.instance or ReglaDisponibilidadRecurrente()
        for clave, valor in attrs.items():
            setattr(instancia, clave, valor)
        instancia.full_clean()
        return attrs


class ExcepcionDisponibilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcepcionDisponibilidad
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instancia = self.instance or ExcepcionDisponibilidad()
        for clave, valor in attrs.items():
            setattr(instancia, clave, valor)
        instancia.full_clean()
        return attrs


class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instancia = self.instance or Cita()
        for clave, valor in attrs.items():
            setattr(instancia, clave, valor)
        instancia.full_clean()
        return attrs


class ValidarCitaSerializer(serializers.Serializer):
    recurso = serializers.PrimaryKeyRelatedField(queryset=RecursoReservable.objects.all())
    servicio = serializers.PrimaryKeyRelatedField(queryset=Servicio.objects.all())
    inicio = serializers.DateTimeField()
    fin = serializers.DateTimeField()

    def validate(self, attrs):
        cita = Cita(
            recurso=attrs["recurso"],
            servicio=attrs["servicio"],
            inicio=attrs["inicio"],
            fin=attrs["fin"],
            titulo="verificacion",
        )
        cita.full_clean()
        return attrs
