from django.contrib import admin

from .models import Cart, CartItem, CheckIn, Order, OrderItem, Payment


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("producto", "cantidad", "precio_unitario", "total_linea")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tienda", "status", "created_at")
    list_filter = ("status", "tienda")
    search_fields = ("user__username",)
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("producto", "cantidad", "precio_unitario", "total_linea")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tienda", "status", "total", "paid_at", "created_at")
    list_filter = ("status", "tienda")
    search_fields = ("user__username",)
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "provider", "amount", "status", "created_at")
    list_filter = ("status", "provider")
    search_fields = ("order__id",)


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ("id", "producto", "user", "tienda", "status", "created_at", "done_at")
    list_filter = ("status", "tienda")
    search_fields = ("producto__nombre", "user__username")

