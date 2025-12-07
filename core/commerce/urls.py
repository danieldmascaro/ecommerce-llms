from django.urls import path

from .views import (
    ActiveCartView,
    CartItemAddView,
    CartItemDetailView,
    CartSummaryView,
    CheckInCompleteView,
    CheckInListView,
    CheckoutView,
    OrderDetailView,
    OrderListView,
    OrderPayView,
)

urlpatterns = [
    path("cart/active/", ActiveCartView.as_view(), name="commerce-cart-active"),
    path("cart/items/", CartItemAddView.as_view(), name="commerce-cart-items"),
    path("cart/items/<int:producto_id>/", CartItemDetailView.as_view(), name="commerce-cart-item-detail"),
    path("cart/summary/", CartSummaryView.as_view(), name="commerce-cart-summary"),
    path("checkout/", CheckoutView.as_view(), name="commerce-checkout"),
    path("orders/", OrderListView.as_view(), name="commerce-orders"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="commerce-order-detail"),
    path("orders/<int:pk>/pay/", OrderPayView.as_view(), name="commerce-order-pay"),
    path("checkins/", CheckInListView.as_view(), name="commerce-checkins"),
    path("checkins/<int:pk>/complete/", CheckInCompleteView.as_view(), name="commerce-checkin-complete"),
]

