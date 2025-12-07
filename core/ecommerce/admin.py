from django.contrib import admin

from .models import Agenda, Categoria, CategoriaTienda, Producto, ProductoCategoria, Tienda
admin.site.register(Tienda)
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(CategoriaTienda)
admin.site.register(ProductoCategoria)
admin.site.register(Agenda)
