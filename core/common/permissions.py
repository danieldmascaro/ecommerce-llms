from rest_framework import permissions


def resolve_owner(obj):
    """
    Resuelve el usuario propietario con duck-typing para evitar registrar modelos uno a uno.
    Orden de resolución:
      1) Método get_owner() en el objeto si existe.
      2) Atributo owner si existe.
      3) Heurísticas comunes (user directo o encadenado por cuenta/tienda/flujo/order/cart/sale_event).
    """
    # Contrato sugerido: los modelos pueden exponer get_owner() o owner.
    get_owner = getattr(obj, "get_owner", None)
    if callable(get_owner):
        try:
            resolved = get_owner()
            if resolved:
                return resolved
        except Exception:
            pass

    direct_owner = getattr(obj, "owner", None)
    if direct_owner:
        return direct_owner

    paths = [
        ("user",),
        ("cuenta", "user"),
        ("tienda", "cuenta", "user"),
        ("flujo_agente", "tienda", "cuenta", "user"),
        ("order", "user"),
        ("cart", "user"),
        ("sale_event", "user"),
    ]
    for path in paths:
        current = obj
        for attr in path:
            current = getattr(current, attr, None)
            if current is None:
                break
        else:
            return current
    return None


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permite acceso total a admin. Para usuarios normales,
    restringe a objetos relacionados con su cuenta/tienda.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or user.is_superuser:
            return True
        return resolve_owner(obj) == user


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwner(permissions.BasePermission):
    """
    Permite acceso solo al propietario del objeto (no lo abre a admin/staff por defecto).
    Útil para vistas estrictamente privadas por usuario/cuenta/tienda.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return resolve_owner(obj) == request.user
