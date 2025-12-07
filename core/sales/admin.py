from django.contrib import admin

from .models import SaleEvent, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = (
        "producto",
        "producto_nombre",
        "categoria_snapshot_nombre",
        "cantidad",
        "precio_unitario",
        "total_linea",
    )


@admin.register(SaleEvent)
class SaleEventAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "user", "tienda", "order", "cita", "total_amount", "created_at")
    list_filter = ("source", "tienda")
    search_fields = ("user__username",)
    inlines = [SaleItemInline]

