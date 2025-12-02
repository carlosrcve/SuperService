# SuperService/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Rutas de VISTAS WEB (Registran el namespace 'app_name' (ej: 'domicilios') una vez)
    path('', TemplateView.as_view(template_name='base/home.html'), name='home'),
    path('usuarios/', include('usuarios.urls')),    
    path('transporte/', include('transporte.urls')), 
    path('domicilios/', include('domicilios.urls')), 

    # 2. Rutas de API REST (Registran un namespace NUEVO y ÚNICO para la API)
    path('api/v1/usuarios/', include('usuarios.urls', namespace='usuarios_api')),    # <-- ¡Añadir namespace='usuarios_api'!
    path('api/v1/transporte/', include('transporte.urls', namespace='transporte_api')), # <-- ¡Añadir namespace='transporte_api'!
    path('api/v1/domicilios/', include('domicilios.urls', namespace='domicilios_api')), # <-- ¡Añadir namespace='domicilios_api'!
]

# ----------------------------------------------------------------------
# SERVICIO DE ARCHIVOS ESTÁTICOS Y MEDIA EN MODO DESARROLLO (DEBUG=True)
# ----------------------------------------------------------------------
if settings.DEBUG:
    # Estáticos
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # Media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
