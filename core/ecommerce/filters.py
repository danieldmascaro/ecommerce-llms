import django_filters

from .models import Producto


class ProductoFilter(django_filters.FilterSet):
    categoria_id = django_filters.NumberFilter(field_name="categoria_relaciones__categoria_id")
    nombre = django_filters.CharFilter(field_name="nombre", lookup_expr="icontains")

    class Meta:
        model = Producto
        fields = ["categoria_id", "nombre"]
