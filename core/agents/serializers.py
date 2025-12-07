from rest_framework import serializers

from .models import (
    Agente,
    AgentMessage,
    AgentSession,
    CategoriaFlujoAgente,
    FlujoAgente,
    ModeloIA,
    ProductoFlujoAgente,
    Regla,
    Reglamento,
    TipoAgente,
)


class FlujoAgenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlujoAgente
        fields = "__all__"


class AgenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agente
        fields = "__all__"


class ProductoFlujoAgenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoFlujoAgente
        fields = "__all__"


class CategoriaFlujoAgenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaFlujoAgente
        fields = "__all__"


class ModeloIASerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeloIA
        fields = "__all__"


class TipoAgenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAgente
        fields = "__all__"


class ReglaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regla
        fields = "__all__"


class ReglamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reglamento
        fields = "__all__"


class AgentSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentSession
        fields = "__all__"


class AgentMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentMessage
        fields = "__all__"
