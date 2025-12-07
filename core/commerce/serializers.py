from rest_framework import serializers

from .models import Cart, CartItem, CheckIn, Order, OrderItem, Payment


class CartItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    total_linea = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "producto",
            "producto_nombre",
            "cantidad",
            "precio_unitario",
            "total_linea",
        ]
        read_only_fields = ["precio_unitario", "total_linea", "producto_nombre"]

    def get_total_linea(self, obj):
        return obj.total_linea


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "tienda", "status", "created_at", "updated_at", "items"]
        read_only_fields = ["status", "created_at", "updated_at", "items"]


class AddCartItemSerializer(serializers.Serializer):
    tienda_id = serializers.IntegerField()
    producto_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    tienda_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)


class OrderItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "producto",
            "producto_nombre",
            "cantidad",
            "precio_unitario",
            "total_linea",
            "categoria_snapshot_id",
            "categoria_snapshot_nombre",
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "cart",
            "user",
            "tienda",
            "status",
            "subtotal",
            "total",
            "total_items",
            "paid_at",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["created_at"]


class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckIn
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "done_at"]

