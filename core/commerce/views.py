from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from ecommerce.models import Producto, Tienda
from common.pagination import get_page_number_pagination

from .models import Cart, CheckIn, Order
from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    CheckInSerializer,
    OrderSerializer,
    UpdateCartItemSerializer,
)
from .services import (
    add_item_to_cart,
    cart_summary,
    checkout_cart,
    confirm_payment,
    get_or_create_cart,
    remove_item_from_cart,
    update_item_quantity,
)


def _get_tienda(tienda_id):
    return get_object_or_404(Tienda, pk=tienda_id)


class ActiveCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tienda_id = request.query_params.get("tienda_id")
        if not tienda_id:
            return Response({"detail": "tienda_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        tienda = _get_tienda(tienda_id)
        cart = get_or_create_cart(request.user, tienda)
        data = cart_summary(cart)
        return Response(data)


class CartItemAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto = get_object_or_404(Producto, pk=serializer.validated_data["producto_id"])
        tienda = _get_tienda(serializer.validated_data["tienda_id"])
        quantity = serializer.validated_data["quantity"]
        try:
            cart = add_item_to_cart(request.user, tienda, producto, quantity)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(cart_summary(cart), status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, producto_id: int):
        tienda_id = request.query_params.get("tienda_id") or request.data.get("tienda_id")
        if not tienda_id:
            return Response({"detail": "tienda_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UpdateCartItemSerializer(
            data={"tienda_id": tienda_id, "quantity": request.data.get("quantity", 0)}
        )
        serializer.is_valid(raise_exception=True)
        tienda = _get_tienda(serializer.validated_data["tienda_id"])
        producto = get_object_or_404(Producto, pk=producto_id)
        try:
            cart = update_item_quantity(request.user, tienda, producto, serializer.validated_data["quantity"])
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(cart_summary(cart))

    def delete(self, request, producto_id: int):
        tienda_id = request.query_params.get("tienda_id") or request.data.get("tienda_id")
        if not tienda_id:
            return Response({"detail": "tienda_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        tienda = _get_tienda(tienda_id)
        producto = get_object_or_404(Producto, pk=producto_id)
        cart = remove_item_from_cart(request.user, tienda, producto)
        return Response(cart_summary(cart), status=status.HTTP_200_OK)


class CartSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tienda_id = request.query_params.get("tienda_id")
        if not tienda_id:
            return Response({"detail": "tienda_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        tienda = _get_tienda(tienda_id)
        cart = get_or_create_cart(request.user, tienda)
        return Response(cart_summary(cart))


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        tienda_id = request.data.get("tienda_id") or request.query_params.get("tienda_id")
        if not tienda_id:
            return Response({"detail": "tienda_id es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        tienda = _get_tienda(tienda_id)
        try:
            order = checkout_cart(request.user, tienda)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(20)

    def get_queryset(self):
        qs = Order.objects.select_related("tienda", "user").prefetch_related("items").order_by("-created_at")
        tienda_id = self.request.query_params.get("tienda_id")
        if tienda_id:
            qs = qs.filter(tienda_id=tienda_id)
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.select_related("tienda", "user").prefetch_related("items")
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


class OrderPayView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        order = get_object_or_404(Order, pk=pk)
        if not request.user.is_staff and order.user != request.user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        provider = request.data.get("provider")
        if not provider:
            return Response({"detail": "provider es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            confirm_payment(order, provider, request.data.get("external_id"), request.data.get("raw_response"))
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)


class CheckInListView(generics.ListAPIView):
    serializer_class = CheckInSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_page_number_pagination(20)

    def get_queryset(self):
        qs = CheckIn.objects.select_related("producto", "tienda", "order_item", "cita").order_by("-created_at")
        tienda_id = self.request.query_params.get("tienda_id")
        if tienda_id:
            qs = qs.filter(tienda_id=tienda_id)
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


class CheckInCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        checkin = get_object_or_404(CheckIn, pk=pk)
        if not request.user.is_staff and checkin.user != request.user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if checkin.status == CheckIn.Status.COMPLETADO:
            return Response({"detail": "Check-in ya completado."})
        checkin.status = CheckIn.Status.COMPLETADO
        checkin.done_at = timezone.now()
        checkin.save(update_fields=["status", "done_at", "updated_at"])
        return Response(CheckInSerializer(checkin).data)
