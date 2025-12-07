from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.pagination import get_page_number_pagination

from .models import (
    Cita,
    ExcepcionDisponibilidad,
    ReglaDisponibilidadRecurrente,
    RecursoReservable,
    Servicio,
)
from .serializers import (
    CitaSerializer,
    ExcepcionDisponibilidadSerializer,
    ReglaDisponibilidadRecurrenteSerializer,
    RecursoReservableSerializer,
    ServicioSerializer,
    ValidarCitaSerializer,
)


class RecursoReservableViewSet(viewsets.ModelViewSet):
    serializer_class = RecursoReservableSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(20)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre", "creado_en", "actualizado_en"]
    filterset_fields = ["esta_activo"]
    queryset = RecursoReservable.objects.all().order_by("nombre", "id")


class ServicioViewSet(viewsets.ModelViewSet):
    serializer_class = ServicioSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(20)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre", "duracion", "creado_en"]
    filterset_fields = ["recurso", "esta_activo"]
    queryset = Servicio.objects.select_related("recurso").all().order_by("id")


class ReglaDisponibilidadRecurrenteViewSet(viewsets.ModelViewSet):
    serializer_class = ReglaDisponibilidadRecurrenteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(50)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["dia_semana", "hora_inicio", "hora_fin"]
    filterset_fields = ["recurso", "servicio", "dia_semana", "esta_activa"]
    queryset = ReglaDisponibilidadRecurrente.objects.select_related("recurso", "servicio").all().order_by(
        "recurso_id", "dia_semana", "hora_inicio", "id"
    )


class ExcepcionDisponibilidadViewSet(viewsets.ModelViewSet):
    serializer_class = ExcepcionDisponibilidadSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(50)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["fecha", "hora_inicio", "hora_fin"]
    filterset_fields = ["recurso", "servicio", "fecha", "tipo", "esta_activa"]
    queryset = ExcepcionDisponibilidad.objects.select_related("recurso", "servicio").all().order_by(
        "-fecha", "hora_inicio", "id"
    )


class CitaViewSet(viewsets.ModelViewSet):
    serializer_class = CitaSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(20)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["inicio", "fin", "creado_en"]
    filterset_fields = {
        "recurso": ["exact"],
        "servicio": ["exact"],
        "estado": ["exact"],
        "producto": ["exact", "isnull"],
        "inicio": ["gte", "lte"],
        "fin": ["gte", "lte"],
    }
    queryset = Cita.objects.select_related("recurso", "servicio").all().order_by("-inicio", "-id")

    @action(detail=False, methods=["post"], url_path="validar-espacio")
    def validar_espacio(self, request):
        serializer = ValidarCitaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Intervalo disponible para agendar."})

    @action(detail=True, methods=["post"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        cita = self.get_object()
        if cita.estado == Cita.Estado.CANCELADA:
            return Response({"detail": "La cita ya esta cancelada."}, status=status.HTTP_400_BAD_REQUEST)
        cita.estado = Cita.Estado.CANCELADA
        cita.save(update_fields=["estado", "actualizado_en"])
        return Response({"detail": "Cita cancelada."})
