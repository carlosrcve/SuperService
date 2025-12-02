from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Comercio)
admin.site.register(Producto)
admin.site.register(Pedido)
admin.site.register(ItemPedido)