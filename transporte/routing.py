# transporte/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Usa 'viaje_id' para que el consumer lo obtenga
    re_path(r'ws/viaje/(?P<viaje_id>\d+)/$', consumers.ViajeChatConsumer.as_asgi()),
]