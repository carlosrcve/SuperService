# transporte/urls.py (Versión Combinada)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    VehiculoViewSet, 
    ViajeViewSet, 
    SolicitudAsistenciaViewSet, 
    MensajeViajeViewSet
)

# 🔑 NECESARIO: Define el namespace 'transporte'
app_name = 'transporte'

# 1. CONFIGURACIÓN DEL ROUTER DRF PARA LA API
router = DefaultRouter()
router.register(r'vehiculos', VehiculoViewSet)
router.register(r'viajes', ViajeViewSet)
router.register(r'asistencias', SolicitudAsistenciaViewSet)
router.register(r'mensajes', MensajeViajeViewSet)

# 2. DEFINICIÓN DE RUTAS WEB (Lista Inicial)
urlpatterns = [
    # -----------------------------------------------------------
    # URLs de Clientes (Solicitud de Servicios)
    # -----------------------------------------------------------
    # 1. Solicitud de Viajes
    path('viaje/solicitar/', views.SolicitarViajeView.as_view(), name='solicitar_viaje'), # <-- ¡Esta ruta vuelve a existir!
    path('viaje/estado/<int:solicitud_id>/', views.ViajePendienteView.as_view(), name='viaje_estado'),
    
    # 2. Solicitud de Asistencia Vial
    path('asistencia/solicitar/', views.SolicitarAsistenciaView.as_view(), name='solicitar_asistencia'),
    path('asistencia/estado/<int:asistencia_id>/', views.ViajePendienteView.as_view(), name='asistencia_pendiente'),
    
    # -----------------------------------------------------------
    # URLs de Conductores y Administración
    # -----------------------------------------------------------
    path('conductor/dashboard/', views.ConductorDashboardView.as_view(), name='conductor_dashboard'),
    path('conductor/vehiculo/registrar/', views.VehiculoRegistroView.as_view(), name='registrar_vehiculo'),
    path('aceptar/<str:tipo_solicitud>/<int:solicitud_id>/', views.AceptarSolicitudView.as_view(), name='aceptar_solicitud'),
    path('admin/vehiculos/pendientes/', views.AdminAprobacionVehiculosView.as_view(), name='admin_aprobacion_vehiculos'),
    path('admin/vehiculos/aprobar/<int:vehiculo_id>/', views.AprobarVehiculoView.as_view(), name='aprobar_vehiculo'),
    path('asistencia/finalizar/<int:asistencia_id>/', views.FinalizarAsistenciaView.as_view(), name='finalizar_asistencia'),
    path('conductor/toggle-disponibilidad/', views.ToggleDisponibilidadView.as_view(), name='toggle_disponibilidad'),
    path('viaje/<int:viaje_id>/', views.ViajeDetailView.as_view(), name='viaje_detalle'),
]

# 3. AÑADIR RUTAS DE LA API: Concatenamos la lista existente con las rutas del router.
urlpatterns += [
    path('', include(router.urls)), 
]