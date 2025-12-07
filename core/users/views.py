from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from common.pagination import get_page_number_pagination
from common.permissions import IsAdminOrOwner

from .models import Cuenta
from .serializers import CuentaSerializer


class CuentaViewSet(viewsets.ModelViewSet):
    serializer_class = CuentaSerializer
    permission_classes = [IsAdminOrOwner]
    pagination_class = get_page_number_pagination(10)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["id", "nombre"]

    def get_queryset(self):
        qs = Cuenta.objects.select_related("user").order_by("id")
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            serializer.save(user=self.request.user)
