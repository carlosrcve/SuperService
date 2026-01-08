from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Rutas de VISTAS WEB
    path('', TemplateView.as_view(template_name='base/home.html'), name='home'),
    path('usuarios/', include('usuarios.urls')),    
    path('transporte/', include('transporte.urls')), 
    path('domicilios/', include('domicilios.urls')), 

    # 2. Rutas de API REST
    
    # 🛑 NUEVA RUTA DE AUTENTICACIÓN: Esta ruta maneja el login, registro y más.
    # Asume que tienes un archivo de urls para la autenticación dentro del app 'usuarios' 
    # o que estás usando un paquete como djoser o rest_auth bajo el prefijo 'api/'.
    # Si tu login está definido en 'usuarios.urls', esta línea es necesaria.
    path('api/', include('usuarios.urls', namespace='auth_api')), 
    
    path('api/v1/usuarios/', include('usuarios.urls', namespace='usuarios_api')),   
    path('api/v1/transporte/', include('transporte.urls', namespace='transporte_api')), 
    path('api/v1/domicilios/', include('domicilios.urls', namespace='domicilios_api')), 
]

# ----------------------------------------------------------------------
# SERVICIO DE ARCHIVOS ESTÁTICOS Y MEDIA EN MODO DESARROLLO (DEBUG=True)
# ----------------------------------------------------------------------
if settings.DEBUG:
    # Estáticos
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # Media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
