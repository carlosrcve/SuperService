#b. Enrutamiento de WebSockets: usuarios/routing.py



# NOTA: Debes agregar esto al archivo asgi.py principal de tu proyecto.


# usuarios/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
