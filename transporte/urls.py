# transporte/urls.py (Versión Combinada)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views  # Importamos el módulo completo para las vistas de clase (.as_view)

# 🔑 NECESARIO: Define el namespace 'transporte'
app_name = 'transporte'

# 1. CONFIGURACIÓN DEL ROUTER DRF PARA LA API
# Registramos aquí los ViewSets que están dentro de views.py
router = DefaultRouter()
router.register(r'vehiculos', views.VehiculoViewSet, basename='vehiculo')
router.register(r'viajes', views.ViajeViewSet, basename='viaje')
router.register(r'asistencias', views.SolicitudAsistenciaViewSet, basename='asistencia')
router.register(r'mensajes', views.MensajeViajeViewSet, basename='mensaje')

# 2. DEFINICIÓN DE RUTAS (Web + API)
urlpatterns = [
    # --- RUTAS DE LA API (Para el celular de Norbe) ---
    path('api/', include(router.urls)), 

    # --- RUTAS WEB (Vistas HTML) ---
    path('viaje/solicitar/', views.SolicitarViajeView.as_view(), name='solicitar_viaje'),
    path('viaje/estado/<int:solicitud_id>/', views.ViajePendienteView.as_view(), name='viaje_estado'),
    path('asistencia/solicitar/', views.SolicitarAsistenciaView.as_view(), name='solicitar_asistencia'),
    path('asistencia/estado/<int:asistencia_id>/', views.ViajePendienteView.as_view(), name='asistencia_pendiente'),
    path('conductor/dashboard/', views.ConductorDashboardView.as_view(), name='conductor_dashboard'),
    path('conductor/vehiculo/registrar/', views.VehiculoRegistroView.as_view(), name='registrar_vehiculo'),
    path('aceptar/<str:tipo_solicitud>/<int:solicitud_id>/', views.AceptarSolicitudView.as_view(), name='aceptar_solicitud'),
    path('admin/vehiculos/pendientes/', views.AdminAprobacionVehiculosView.as_view(), name='admin_aprobacion_vehiculos'),
    path('admin/vehiculos/aprobar/<int:vehiculo_id>/', views.AprobarVehiculoView.as_view(), name='aprobar_vehiculo'),
    path('asistencia/finalizar/<int:asistencia_id>/', views.FinalizarAsistenciaView.as_view(), name='finalizar_asistencia'),
    path('conductor/toggle-disponibilidad/', views.ToggleDisponibilidadView.as_view(), name='toggle_disponibilidad'),
    path('viaje/<int:viaje_id>/', views.ViajeDetailView.as_view(), name='viaje_detalle'),
]