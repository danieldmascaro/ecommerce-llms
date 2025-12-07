from django.contrib import admin

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

admin.site.register(ModeloIA)
admin.site.register(TipoAgente)
admin.site.register(Reglamento)
admin.site.register(Regla)
admin.site.register(FlujoAgente)
admin.site.register(ProductoFlujoAgente)
admin.site.register(CategoriaFlujoAgente)
admin.site.register(Agente)
admin.site.register(AgentSession)
admin.site.register(AgentMessage)
