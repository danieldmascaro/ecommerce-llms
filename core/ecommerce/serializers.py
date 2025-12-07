from rest_framework import serializers

from .models import Agenda, Categoria, CategoriaTienda, Producto, ProductoCategoria, Tienda


class TiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tienda
        fields = "__all__"


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = "__all__"


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class CategoriaTiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaTienda
        fields = "__all__"


class ProductoCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoCategoria
        fields = "__all__"


class AgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agenda
        fields = "__all__"

