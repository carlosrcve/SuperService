# usuarios/urls.py

# usuarios/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import UsuarioViewSet # Se importa la clase ViewSet para usar .as_view()


app_name = 'usuarios'


# ----------------------------------------------------------------------
# 1. DEFINICIÓN DE VISTA CUSTOM (SOLUCIÓN AL NameError)
# ----------------------------------------------------------------------
# Convierte el método 'obtener_perfil' del ViewSet en una vista ejecutable 
# que maneja peticiones GET. ESTA LÍNEA ES LA CRÍTICA QUE FALTABA.
perfil_obtener_view = UsuarioViewSet.as_view({'get': 'obtener_perfil'})


# ----------------------------------------------------------------------
# 2. CONFIGURACIÓN DEL ROUTER DRF PARA LA API
# ----------------------------------------------------------------------
router = DefaultRouter()
# Registra el ViewSet. Las rutas generadas son /usuarios/, /usuarios/{pk}/, 
# /usuarios/registrar_conductor/, y /usuarios/obtener_perfil/
router.register(r'', views.UsuarioViewSet, basename='usuario-api') 


# ----------------------------------------------------------------------
# 3. DEFINICIÓN DE PATRONES DE URL (urlpatterns)
# ----------------------------------------------------------------------
urlpatterns = [
    
    # A. Rutas de VISTAS WEB (Autenticación y Registro)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/cliente/', views.registro_cliente_view, name='registro_cliente'),
    path('registro/conductor/', views.registro_conductor_view, name='registro_conductor'),
    
    # B. Rutas de VISTAS WEB (Chat P2P)
    path('chat/', views.chat_list_view, name='chat_inbox'), 
    path('chat/<int:user_id>/', views.chat_room_view, name='chat_room'),
    
    # C. RUTA DE API CUSTOM (SOLUCIÓN AL 404 ORIGINAL)
    # Usa la vista ejecutable definida en el punto 1 para responder a la URL del Frontend.
    # Esta ruta es /usuarios/perfil/obtener/
    path('perfil/obtener/', perfil_obtener_view, name='perfil-obtener-custom'), 
    
    # D. Rutas del DRF Router (Rutas automáticas)
    # Debe ir al final. Las rutas generadas usan el prefijo definido en el urls.py principal.
    path('', include(router.urls)),
]