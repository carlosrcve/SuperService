# domicilios/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Ruta: ws://127.0.0.1:8081/ws/pedido/<int:pedido_id>/
    re_path(r'ws/pedido/(?P<pedido_id>\d+)/$', consumers.PedidoChatConsumer.as_asgi()),
]