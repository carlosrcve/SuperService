# usuarios/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import UsuarioViewSet

# 1. 🔑 CORRECCIÓN CRÍTICA: La variable 'app_name' estaba mal escrita.
app_name = 'usuarios' # Debe ser 'app_name', no 'pp_name'

# --- 2. CONFIGURACIÓN DEL ROUTER DRF PARA LA API ---
router = DefaultRouter()
# ✅ Correcto: Al usar r'' aquí, la URL de la API será más limpia.
router.register(r'', views.UsuarioViewSet, basename='usuario-api') 

# --- 3. DEFINICIÓN DE PATRONES DE URL (Web y API combinadas) ---
urlpatterns = [
    
    # A. Rutas de VISTAS WEB (Autenticación y Registro)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/cliente/', views.registro_cliente_view, name='registro_cliente'),
    path('registro/conductor/', views.registro_conductor_view, name='registro_conductor'),
    
    # B. Rutas de VISTAS WEB (Chat P2P)
    path('chat/', views.chat_list_view, name='chat_inbox'), 
    path('chat/<int:user_id>/', views.chat_room_view, name='chat_room'),
    
    # C. Rutas de API REST (DRF Router)
    # Se incluye el router al final para que use el prefijo de ruta (ej: /api/v1/usuarios/)
    path('', include(router.urls)),
]



'''
from django.urls import path
from . import views

urlpatterns = [
    # Rutas de Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/cliente/', views.registro_cliente_view, name='registro_cliente'),
    path('registro/conductor/', views.registro_conductor_view, name='registro_conductor'),
    
    # Rutas de CHAT
    # 1. Lista de usuarios disponibles para chatear
    path('chat/', views.chat_list_view, name='chat_list'),
    # 2. Sala de chat específica con un usuario por ID
    path('chat/<int:user_id>/', views.chat_room_view, name='chat_room'),
    path('chat/inbox/', views.chat_list_view, name='chat_inbox'),
    #path('chat/room/<int:user_id>/', views.chat_room_view, name='chat_room'),
]

# NOTA: Debes incluir este archivo en el archivo urls.py principal de tu proyecto.


# usuarios/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PerfilUsuarioViewSet

router = DefaultRouter()
# Registra tu ViewSet. Esto crea URLs como: 
# /usuarios/ y /usuarios/{pk}/
router.register(r'usuarios', PerfilUsuarioViewSet) 

urlpatterns = [
    path('', include(router.urls)), # Incluye todas las rutas generadas por el router
]
'''