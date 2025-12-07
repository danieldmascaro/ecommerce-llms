from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.pagination import get_page_number_pagination
from common.permissions import IsAdminOrOwner

from .filters import ProductoFilter
from .models import Agenda, Categoria, CategoriaTienda, Producto, ProductoCategoria, Tienda
from .serializers import (
    AgendaSerializer,
    CategoriaSerializer,
    CategoriaTiendaSerializer,
    ProductoCategoriaSerializer,
    ProductoSerializer,
    TiendaSerializer,
)


class TiendaViewSet(viewsets.ModelViewSet):
    serializer_class = TiendaSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(10)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "id"]

    def get_queryset(self):
        qs = Tienda.objects.select_related("cuenta", "cuenta__user").order_by("id")
        if self.request.user.is_staff:
            return qs
        return qs.filter(cuenta__user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            serializer.save(cuenta=self.request.user.cuenta)


class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(10)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "id"]

    def get_queryset(self):
        qs = Categoria.objects.all().order_by("id")
        if self.request.user.is_staff:
            return qs
        # Categorias vinculadas a tiendas del usuario
        return qs.filter(categoriatienda__tienda__cuenta__user=self.request.user).distinct()


class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(20)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductoFilter
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "precio", "id"]

    def get_queryset(self):
        qs = Producto.objects.all().order_by("id")
        user = self.request.user

        if not user.is_staff:
            qs = qs.filter(categoria_relaciones__categoria__categoriatienda__tienda__cuenta__user=user).distinct()

        return qs.distinct()

    @action(detail=False, methods=["get"], url_path="total")
    def total(self, request):
        """Devuelve total de productos accesibles por el usuario autenticado."""
        total = self.filter_queryset(self.get_queryset()).count()
        return Response({"total": total})

    @action(detail=False, methods=["get"], url_path="por-categoria")
    def por_categoria(self, request):
        """Lista productos filtrados por categoria_id, restringidos al usuario autenticado."""
        categoria_id = request.query_params.get("categoria_id")
        if not categoria_id:
            return Response({"detail": "categoria_id es requerido"}, status=400)
        qs = self.filter_queryset(self.get_queryset()).filter(categoria_relaciones__categoria_id=categoria_id).distinct()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ProductoCategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoCategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(20)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["id", "producto_id", "categoria_id"]

    def get_queryset(self):
        qs = ProductoCategoria.objects.select_related("producto", "categoria").order_by("id")
        if self.request.user.is_staff:
            return qs
        return qs.filter(categoria__categoriatienda__tienda__cuenta__user=self.request.user).distinct()


class CategoriaTiendaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaTiendaSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(20)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["id", "categoria_id", "tienda_id"]

    def get_queryset(self):
        qs = CategoriaTienda.objects.select_related("categoria", "tienda").order_by("id")
        if self.request.user.is_staff:
            return qs
        return qs.filter(tienda__cuenta__user=self.request.user)


class AgendaViewSet(viewsets.ModelViewSet):
    serializer_class = AgendaSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(10)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["inicio", "fin", "id"]

    def get_queryset(self):
        qs = Agenda.objects.select_related("producto").order_by("inicio", "id")
        if self.request.user.is_staff:
            return qs
        return qs.filter(
            producto__categoria_relaciones__categoria__categoriatienda__tienda__cuenta__user=self.request.user
        ).distinct()
