from decimal import Decimal

from django.db.models import Sum
from django.utils.dateparse import parse_date
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import get_page_number_pagination
from common.permissions import IsAdminOrOwner

from .models import SaleEvent, SaleItem
from .serializers import SaleEventSerializer


class SalesSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        group_by = request.query_params.get("group_by", "producto")
        qs = SaleItem.objects.select_related("sale_event")
        tienda_id = request.query_params.get("tienda_id")
        if tienda_id:
            qs = qs.filter(sale_event__tienda_id=tienda_id)

        desde = request.query_params.get("desde")
        hasta = request.query_params.get("hasta")
        if desde:
            fecha = parse_date(desde)
            if fecha:
                qs = qs.filter(sale_event__created_at__date__gte=fecha)
        if hasta:
            fecha = parse_date(hasta)
            if fecha:
                qs = qs.filter(sale_event__created_at__date__lte=fecha)

        if group_by == "categoria":
            data = (
                qs.values("categoria_snapshot_id", "categoria_snapshot_nombre")
                .annotate(unidades=Sum("cantidad"), revenue=Sum("total_linea"))
                .order_by("-revenue")
            )
            respuesta = [
                {
                    "key": item["categoria_snapshot_nombre"] or f"categoria-{item['categoria_snapshot_id']}",
                    "unidades": item["unidades"] or 0,
                    "revenue": item["revenue"] or Decimal("0"),
                }
                for item in data
            ]
        else:
            data = (
                qs.values("producto_id", "producto_nombre")
                .annotate(unidades=Sum("cantidad"), revenue=Sum("total_linea"))
                .order_by("-revenue")
            )
            respuesta = [
                {
                    "key": item["producto_nombre"] or f"producto-{item['producto_id']}",
                    "unidades": item["unidades"] or 0,
                    "revenue": item["revenue"] or Decimal("0"),
                }
                for item in data
            ]
        return Response(respuesta)


class SaleEventListView(generics.ListAPIView):
    serializer_class = SaleEventSerializer
    permission_classes = [IsAdminOrOwner]
    pagination_class = get_page_number_pagination(20)

    def get_queryset(self):
        qs = SaleEvent.objects.select_related("tienda", "user", "order", "cita").prefetch_related("items").order_by(
            "-created_at"
        )
        tienda_id = self.request.query_params.get("tienda_id")
        if tienda_id:
            qs = qs.filter(tienda_id=tienda_id)
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


class SaleEventDetailView(generics.RetrieveAPIView):
    serializer_class = SaleEventSerializer
    permission_classes = [IsAdminOrOwner]

    def get_queryset(self):
        qs = SaleEvent.objects.select_related("tienda", "user", "order", "cita").prefetch_related("items")
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)
