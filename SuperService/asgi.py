"""
ASGI config for SuperService project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""
'''
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SuperService.settings')

application = get_asgi_application()
'''





# SuperService/asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 1. Configurar el entorno de Django PRIMERO
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SuperService.settings')

# 2. Llamar a get_asgi_application()
# Esta función asegura que las Apps se carguen completamente.
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application() # Guardamos la aplicación HTTP/WSGI

# 3. Importar los módulos de routing AHORA (después de cargar las apps)
import usuarios.routing
import transporte.routing
import domicilios.routing # <--- ¡CORRECCIÓN AQUÍ

# 4. Definición de la aplicación principal
application = ProtocolTypeRouter({
    # El tráfico HTTP se maneja con la aplicación ASGI de Django
    "http": django_asgi_app, 
    
    # El tráfico WebSocket se maneja con el router de Channels
    "websocket": AuthMiddlewareStack(
        URLRouter(
            usuarios.routing.websocket_urlpatterns + 
            transporte.routing.websocket_urlpatterns +
            domicilios.routing.websocket_urlpatterns # <--- ¡Nuevo!
        )
    ),
})