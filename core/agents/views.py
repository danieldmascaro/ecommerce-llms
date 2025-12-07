from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from common.pagination import get_page_number_pagination
from common.permissions import IsAdminOrReadOnly

from .models import (
    Agente,
    AgentMessage,
    AgentSession,
    CategoriaFlujoAgente,
    FlujoAgente,
    ModeloIA,
    ProductoFlujoAgente,
    Regla,
    Reglamento,
    TipoAgente,
)
from .serializers import (
    AgenteSerializer,
    AgentMessageSerializer,
    AgentSessionSerializer,
    CategoriaFlujoAgenteSerializer,
    FlujoAgenteSerializer,
    ModeloIASerializer,
    ProductoFlujoAgenteSerializer,
    ReglaSerializer,
    ReglamentoSerializer,
    TipoAgenteSerializer,
)


class FlujoAgenteViewSet(viewsets.ModelViewSet):
    serializer_class = FlujoAgenteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(10)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "nombre_comercial"]
    ordering_fields = ["nombre", "nombre_comercial", "id"]

    def get_queryset(self):
        qs = (
            FlujoAgente.objects.select_related("tienda", "tienda__cuenta", "tienda__cuenta__user").order_by("id")
        )
        if self.request.user.is_staff:
            return qs
        return qs.filter(tienda__cuenta__user=self.request.user)


class AgenteViewSet(viewsets.ModelViewSet):
    serializer_class = AgenteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(10)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "id"]

    def get_queryset(self):
        qs = (
            Agente.objects.select_related(
                "tienda",
                "tienda__cuenta",
                "tienda__cuenta__user",
                "flujo_agente",
                "tipo_agente",
                "modelo_ia",
                "reglamento",
            ).order_by("id")
        )
        if self.request.user.is_staff:
            return qs
        return qs.filter(tienda__cuenta__user=self.request.user)


class ProductoFlujoAgenteViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoFlujoAgenteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(20)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["id", "producto_id", "flujo_agente_id"]

    def get_queryset(self):
        qs = ProductoFlujoAgente.objects.select_related("producto", "flujo_agente").order_by("id")
        if self.request.user.is_staff:
            return qs
        return qs.filter(flujo_agente__tienda__cuenta__user=self.request.user)


class CategoriaFlujoAgenteViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaFlujoAgenteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(20)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["id", "categoria_id", "flujo_agente_id"]

    def get_queryset(self):
        qs = CategoriaFlujoAgente.objects.select_related("categoria", "flujo_agente").order_by("id")
        if self.request.user.is_staff:
            return qs
        return qs.filter(flujo_agente__tienda__cuenta__user=self.request.user)


class ModeloIAViewSet(viewsets.ModelViewSet):
    serializer_class = ModeloIASerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = get_page_number_pagination(10)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "id"]
    queryset = ModeloIA.objects.all().order_by("id")


class TipoAgenteViewSet(viewsets.ModelViewSet):
    serializer_class = TipoAgenteSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = get_page_number_pagination(10)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "id"]
    queryset = TipoAgente.objects.all().order_by("id")


class AgentSessionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AgentSessionSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = get_page_number_pagination(20)
    queryset = AgentSession.objects.all().order_by("-created_at")


class AgentMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AgentMessageSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = get_page_number_pagination(20)
    queryset = AgentMessage.objects.select_related("session").all().order_by("-created_at", "-id")


class ReglaViewSet(viewsets.ModelViewSet):
    serializer_class = ReglaSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = get_page_number_pagination(10)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["texto"]
    ordering_fields = ["orden", "id"]
    queryset = Regla.objects.all().order_by("id")


class ReglamentoViewSet(viewsets.ModelViewSet):
    serializer_class = ReglamentoSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = get_page_number_pagination(10)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "id"]
    queryset = Reglamento.objects.all().order_by("id")
