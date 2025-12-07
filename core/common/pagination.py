from rest_framework.pagination import PageNumberPagination


def get_page_number_pagination(page_size: int = 20, max_page_size: int = 100):
    """
    Devuelve una clase de paginación PageNumberPagination parametrizable.
    page_size: cantidad de elementos por página por defecto.
    max_page_size: límite superior configurable via query param page_size.
    """
    attrs = {
        "page_size": page_size,
        "page_size_query_param": "page_size",
        "max_page_size": max_page_size,
    }
    return type("DynamicPageNumberPagination", (PageNumberPagination,), attrs)
