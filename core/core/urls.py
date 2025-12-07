"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from agents.views import (
    AgenteViewSet,
    AgentMessageViewSet,
    AgentSessionViewSet,
    CategoriaFlujoAgenteViewSet,
    FlujoAgenteViewSet,
    ModeloIAViewSet,
    ProductoFlujoAgenteViewSet,
    ReglaViewSet,
    ReglamentoViewSet,
    TipoAgenteViewSet,
)
from commerce import urls as commerce_urls
from ecommerce.views import (
    AgendaViewSet,
    CategoriaTiendaViewSet,
    CategoriaViewSet,
    ProductoCategoriaViewSet,
    ProductoViewSet,
    TiendaViewSet,
)
from users.views import CuentaViewSet
from sales import urls as sales_urls
from scheduling.views import (
    CitaViewSet,
    ExcepcionDisponibilidadViewSet,
    ReglaDisponibilidadRecurrenteViewSet,
    RecursoReservableViewSet,
    ServicioViewSet,
)

router = routers.DefaultRouter()
router.register(r'cuentas', CuentaViewSet, basename='cuentas')
router.register(r'tiendas', TiendaViewSet, basename='tiendas')
router.register(r'flujos', FlujoAgenteViewSet, basename='flujos')
router.register(r'agentes', AgenteViewSet, basename='agentes')
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'productos', ProductoViewSet, basename='productos')
router.register(r'producto-categorias', ProductoCategoriaViewSet, basename='producto-categorias')
router.register(r'producto-flujos', ProductoFlujoAgenteViewSet, basename='producto-flujos')
router.register(r'categoria-flujos', CategoriaFlujoAgenteViewSet, basename='categoria-flujos')
router.register(r'categoria-tiendas', CategoriaTiendaViewSet, basename='categoria-tiendas')
router.register(r'agendas', AgendaViewSet, basename='agendas')
router.register(r'reglas', ReglaViewSet, basename='reglas')
router.register(r'reglamentos', ReglamentoViewSet, basename='reglamentos')
router.register(r'modelos-ia', ModeloIAViewSet, basename='modelos-ia')
router.register(r'tipos-agente', TipoAgenteViewSet, basename='tipos-agente')
router.register(r'agent-sessions', AgentSessionViewSet, basename='agent-sessions')
router.register(r'agent-messages', AgentMessageViewSet, basename='agent-messages')
router.register(r'recursos', RecursoReservableViewSet, basename='recursos')
router.register(r'servicios', ServicioViewSet, basename='servicios')
router.register(r'reglas-disponibilidad', ReglaDisponibilidadRecurrenteViewSet, basename='reglas-disponibilidad')
router.register(r'excepciones-disponibilidad', ExcepcionDisponibilidadViewSet, basename='excepciones-disponibilidad')
router.register(r'citas', CitaViewSet, basename='citas')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api/', include(router.urls)),
    path('api/commerce/', include(commerce_urls)),
    path('api/sales/', include(sales_urls)),
]
