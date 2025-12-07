from rest_framework import serializers

from .models import SaleEvent, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = [
            "producto",
            "producto_nombre",
            "categoria_snapshot_id",
            "categoria_snapshot_nombre",
            "cantidad",
            "precio_unitario",
            "total_linea",
        ]
        read_only_fields = fields


class SaleEventSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)

    class Meta:
        model = SaleEvent
        fields = [
            "id",
            "user",
            "tienda",
            "source",
            "order",
            "cita",
            "total_amount",
            "total_items",
            "created_at",
            "items",
        ]
        read_only_fields = fields


class SalesSummaryItemSerializer(serializers.Serializer):
    key = serializers.CharField()
    unidades = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)

