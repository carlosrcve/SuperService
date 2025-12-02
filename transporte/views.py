# transporte/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import DetailView # Se mantiene si se usa en otras vistas

from .forms import (
    ViajeSolicitudForm, 
    VehiculoRegistroForm, 
    AsistenciaSolicitudForm, 
    MensajeViajeForm # 🔑 Importación de formulario de chat
)
from .models import (
    Viaje, 
    Vehiculo, 
    SolicitudAsistencia, 
    MensajeViaje # 🔑 Importación de modelo de chat
)


# ----------------------------------------------------------------------
# Mixins de Verificación de Roles
# ----------------------------------------------------------------------

class ClienteRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verifica que el usuario esté logueado y tenga el rol 'cliente'."""
    def test_func(self):
        # Asume que el modelo de usuario tiene un campo 'rol'
        return self.request.user.is_authenticated and self.request.user.rol == 'cliente'
    
    def handle_no_permission(self):
        messages.error(self.request, "Solo los clientes pueden acceder a esta función.")
        return redirect('home')

class ConductorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verifica que el usuario esté logueado y tenga el rol 'conductor' y esté disponible."""
    def test_func(self):
        user = self.request.user
        # Se requiere rol 'conductor' o 'repartidor_domicilios' y que la cuenta esté marcada como disponible
        return user.is_authenticated and user.rol in ['conductor', 'repartidor_domicilios'] and user.disponible

    def handle_no_permission(self):
        messages.error(self.request, "Debes ser un conductor aprobado y estar 'disponible' para acceder.")
        return redirect('home')

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verifica que el usuario esté logueado y tenga el rol 'administrador'."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.rol == 'administrador'
    
    def handle_no_permission(self):
        messages.error(self.request, "Acceso denegado. Solo administradores pueden acceder a esta función.")
        return redirect('home')


# ----------------------------------------------------------------------
# 1. Vistas para Clientes (Solicitar Servicios)
# ----------------------------------------------------------------------

# transporte/views.py (Sección 1. Vistas para Clientes)

# Definición de estados activos para la búsqueda (Basado en tus opciones de Admin)
# 🚨 LISTA CORREGIDA: Usando los códigos internos de la base de datos.
ESTADOS_ACTIVOS = [
    'solicitado', 
    'aceptado', 
    'en_ruta_origen', 
    'en_curso'
]

class SolicitarViajeView(LoginRequiredMixin, View):
    """
    Maneja la visualización del formulario y el procesamiento de la solicitud de viaje.
    """
    template_name = 'transporte/solicitar_viaje.html'
    
    # -----------------------------------------------------------
    # 1. Método GET: Mostrar el formulario y buscar viaje pendiente (CORREGIDO)
    # -----------------------------------------------------------
    def get(self, request, *args, **kwargs):
        form = ViajeSolicitudForm()
        
        # Búsqueda segura del viaje pendiente más reciente
        viaje_pendiente = Viaje.objects.filter(
            cliente=request.user, 
            estado__in=ESTADOS_ACTIVOS
        ).order_by('-creado_en').first() # .first() devuelve None si no encuentra nada
            
        context = {
            'form': form,
            'viaje': viaje_pendiente # Pasa el objeto viaje (o None) al contexto
        }
        
        return render(request, self.template_name, context)

    # -----------------------------------------------------------
    # 2. Método POST: Procesar la solicitud
    # -----------------------------------------------------------
    def post(self, request, *args, **kwargs):
        form = ViajeSolicitudForm(request.POST)
        
        # 🟢 OBTENER DATOS DEL MAPA (Coordenadas y Nombres)
        origen_data = request.POST.get('origen_lat_lng')
        destino_data = request.POST.get('destino_lat_lng')

        nombre_origen = request.POST.get('nombre_origen', '').strip()
        nombre_destino = request.POST.get('nombre_destino', '').strip()

        # 1. Validar el formulario de Django para los campos estándar
        if form.is_valid():
            
            # --- 2. Validación de Coordenadas ---
            if not origen_data or not destino_data:
                messages.error(request, "Debe seleccionar tanto el **Origen** como el **Destino** en el mapa o mediante la búsqueda.")
                return render(request, self.template_name, {'form': form})

            try:
                # Separar las coordenadas y convertirlas a Decimal
                origen_lat, origen_lon = map(lambda x: Decimal(x.strip()), origen_data.split(','))
                destino_lat, destino_lon = map(lambda x: Decimal(x.strip()), destino_data.split(','))
            except Exception:
                messages.error(request, "Error al procesar las coordenadas. Asegúrese de que la selección sea válida.")
                return render(request, self.template_name, {'form': form})

            # --- 3. Crear y Guardar el objeto Viaje ---
            try:
                # Guardar la instancia (sin cometerla a la BD)
                viaje = form.save(commit=False)
                
                # Asignar el cliente (Usuario logueado)
                viaje.cliente = request.user
                
                # Asignar las coordenadas
                viaje.origen_lat = origen_lat
                viaje.origen_lon = origen_lon
                viaje.destino_lat = destino_lat
                viaje.destino_lon = destino_lon
                
                # Asignar los nombres de dirección
                if hasattr(viaje, 'nombre_origen'):
                    viaje.nombre_origen = nombre_origen
                if hasattr(viaje, 'nombre_destino'):
                    viaje.nombre_destino = nombre_destino
                
                viaje.save() # Guardar el objeto Viaje completo
                
                # Mensaje de éxito
                origen_display = nombre_origen or f"({origen_lat.quantize(Decimal('.000001'))},...)"
                messages.success(request, f"¡Viaje desde **{origen_display}** solicitado exitosamente! Buscando conductor.")
                
                # Redirigir al detalle (Asegúrate de que 'viaje_detalle' exista en tus urls.py)
                return redirect('transporte:viaje_detalle', viaje_id=viaje.id) # Usamos viaje_id, asumiendo que es el parámetro URL
                
            except Exception as e:
                # Puedes usar logging aquí para registrar el error
                messages.error(request, f"Ocurrió un error inesperado al guardar el viaje: {e}")
                return render(request, self.template_name, {'form': form})

        else:
            # Si el formulario de Django falla (p.ej., campos de nota obligatorios)
            messages.error(request, "Por favor, corrija los errores en el formulario de detalles.")
            return render(request, self.template_name, {'form': form})

class SolicitarAsistenciaView(ClienteRequiredMixin, View):
    """Permite a un cliente solicitar asistencia vial."""
    template_name = 'transporte/solicitar_asistencia.html'

    def get(self, request):
        form = AsistenciaSolicitudForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AsistenciaSolicitudForm(request.POST)
        if form.is_valid():
            asistencia = form.save(commit=False)
            asistencia.cliente = request.user
            asistencia.estado = 'solicitado'
            asistencia.save()
            messages.success(request, f'Asistencia vial de {asistencia.get_tipo_asistencia_display()} solicitada. Buscando proveedor...')
            return redirect('asistencia_pendiente', asistencia_id=asistencia.id)
            
        return render(request, self.template_name, {'form': form})

class ViajePendienteView(ClienteRequiredMixin, View):
    """Muestra el estado actual de un viaje o asistencia solicitado por el cliente."""
    
    def get(self, request, solicitud_id):
        # Intenta obtener el Viaje
        try:
            solicitud = Viaje.objects.get(id=solicitud_id, cliente=request.user)
            template_name = 'transporte/viaje_pendiente.html'
        except Viaje.DoesNotExist:
            # Si no es un Viaje, intentamos obtener la SolicitudAsistencia
            solicitud = get_object_or_404(SolicitudAsistencia, id=solicitud_id, cliente=request.user)
            template_name = 'transporte/asistencia_pendiente.html' # Nuevo template para Asistencia

        context = {'solicitud': solicitud}
        return render(request, template_name, context)

# ----------------------------------------------------------------------
# 2. Vistas para Conductores (Gestión de Servicios y Vehículos)
# ----------------------------------------------------------------------

class VehiculoRegistroView(ConductorRequiredMixin, View):
    """Permite a un conductor registrar un vehículo."""
    template_name = 'transporte/registro_vehiculo.html'
    
    def get(self, request):
        if Vehiculo.objects.filter(conductor=request.user).exists():
            messages.info(request, "Ya tienes vehículos registrados. Puedes verlos en tu dashboard.")
            return redirect('conductor_dashboard')
            
        form = VehiculoRegistroForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = VehiculoRegistroForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.conductor = request.user
            vehiculo.aprobado = True # Se asume que el admin debe revisar
            vehiculo.save()
            messages.success(request, 'Vehículo registrado. Pendiente de aprobación administrativa.')
            return redirect('conductor_dashboard')
            
        return render(request, self.template_name, {'form': form})

class ConductorDashboardView(ConductorRequiredMixin, View):
    """Página principal del conductor: Muestra viajes y asistencias pendientes."""
    template_name = 'transporte/conductor_dashboard.html'
    
    def get(self, request):
        # Muestra solicitudes cercanas (Placeholder, la lógica real es compleja)
        solicitudes_cercanas = Viaje.objects.filter(estado='solicitado').exclude(cliente=request.user)[:10] 
        asistencias_cercanas = SolicitudAsistencia.objects.filter(estado='solicitado').exclude(cliente=request.user)[:5]
        vehiculos = Vehiculo.objects.filter(conductor=request.user)

        context = {
            'solicitudes_viaje': solicitudes_cercanas,
            'solicitudes_asistencia': asistencias_cercanas,
            'vehiculos': vehiculos,
        }
        return render(request, self.template_name, context)

class AceptarSolicitudView(ConductorRequiredMixin, View):
    """Permite a un conductor aceptar un Viaje o una SolicitudAsistencia."""
    
    @method_decorator(require_POST)
    def post(self, request, tipo_solicitud, solicitud_id):
        user = request.user
        
        if tipo_solicitud == 'viaje':
            modelo = Viaje
        elif tipo_solicitud == 'asistencia':
            modelo = SolicitudAsistencia
        else:
            messages.error(request, "Tipo de solicitud no válido.")
            return redirect('conductor_dashboard')
            
        solicitud = get_object_or_404(modelo, id=solicitud_id, estado='solicitado')
        
        if tipo_solicitud == 'viaje' and not Vehiculo.objects.filter(conductor=user, aprobado=True).exists():
            messages.error(request, "Debes tener al menos un vehículo aprobado para aceptar viajes.")
            return redirect('conductor_dashboard')
            
        solicitud.estado = 'aceptado'
        
        if tipo_solicitud == 'viaje':
            solicitud.conductor = user 
            solicitud.vehiculo_usado = Vehiculo.objects.filter(conductor=user, aprobado=True).first()
            messages.success(request, f'Has aceptado el Viaje #{solicitud_id}. Dirígete al origen.')
        
        elif tipo_solicitud == 'asistencia':
            solicitud.proveedor = user 
            messages.success(request, f'Has aceptado la Asistencia #{solicitud_id}.')

        solicitud.save()
        return redirect('conductor_dashboard')

class FinalizarAsistenciaView(ConductorRequiredMixin, View):
    """Permite al proveedor marcar una SolicitudAsistencia como completada."""

    @method_decorator(require_POST) 
    def post(self, request, asistencia_id):
        asistencia = get_object_or_404(
            SolicitudAsistencia, 
            pk=asistencia_id, 
            proveedor=request.user, 
            estado__in=['aceptado', 'en_ruta_origen']
        )
        
        asistencia.estado = 'completado'
        asistencia.save()
        
        messages.success(request, f'Servicio de Asistencia #{asistencia_id} marcado como completado.')
        return redirect('conductor_dashboard')

class ToggleDisponibilidadView(LoginRequiredMixin, View):
    """Permite al conductor cambiar su estado de 'disponible' a 'no disponible' y viceversa."""
    
    @method_decorator(require_POST) 
    def dispatch(self, *args, **kwargs):
        # Seguridad manual para permitir que el conductor cambie su estado incluso si NO está disponible
        if self.request.user.rol not in ['conductor', 'repartidor_domicilios']:
             messages.error(self.request, "Acceso denegado.")
             return redirect('home')
             
        return super(ToggleDisponibilidadView, self).dispatch(*args, **kwargs)

    def post(self, request):
        user = request.user
        user.disponible = not user.disponible
        user.save()
        
        if user.disponible:
            messages.success(request, "Tu estado ahora es: **DISPONIBLE**. ¡Puedes recibir solicitudes!")
        else:
            messages.warning(request, "Tu estado ahora es: **NO DISPONIBLE**. No recibirás nuevas solicitudes.")
            
        return redirect('conductor_dashboard')


# ----------------------------------------------------------------------
# 3. Vistas de Detalle (Incluye Chat)
# ----------------------------------------------------------------------

class ViajeDetailView(LoginRequiredMixin, View):
    """
    Muestra el estado, detalles y el chat de un Viaje específico. 
    Asegura que solo el cliente o el conductor puedan acceder.
    Maneja GET (mostrar) y POST (enviar mensaje).
    """
    template_name = 'transporte/viaje_detalle.html'

    def get_object(self, viaje_id):
        # Este método se usa para aplicar la lógica de permisos antes de todo
        user = self.request.user
        
        # 1. Los administradores (is_staff) pueden ver CUALQUIER viaje.
        if user.is_staff:
            return get_object_or_404(Viaje, pk=viaje_id)

        # 2. Los usuarios regulares (cliente o conductor) solo ven sus propios viajes.
        try:
            viaje = Viaje.objects.filter(
                Q(cliente=user) | Q(conductor=user)
            ).get(pk=viaje_id)
        except Viaje.DoesNotExist:
            # Si el objeto no existe O el usuario no es staff ni participante.
            raise Http404("No se encontró el viaje o no tienes permiso para acceder.")
            
        return viaje
    
    # 🛑 CORRECCIÓN: Aceptar 'viaje_id' en lugar de 'pedido_id'
    def get(self, request, viaje_id):
        # 1. Obtener el viaje (la función get_object ya maneja permisos)
        viaje = self.get_object(viaje_id)
        
        # 2. Obtener datos para la plantilla
        # Asumiendo que el related_name del ForeignKey MensajeViaje a Viaje es 'mensajes'
        mensajes = viaje.mensajes.all().order_by('timestamp') 
        form = MensajeViajeForm()

        context = {
            'viaje': viaje,
            'mensajes': mensajes,
            'mensaje_form': form, # El formulario del chat
        }
        return render(request, self.template_name, context)

    # Maneja la solicitud POST (enviar un nuevo mensaje)
    @method_decorator(require_POST)
    def post(self, request, viaje_id):
        # 1. Obtener el viaje (la función get_object ya maneja permisos)
        viaje = self.get_object(viaje_id) 
        form = MensajeViajeForm(request.POST)

        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.viaje = viaje
            mensaje.emisor = request.user 
            mensaje.save()
            messages.success(request, "Mensaje de viaje enviado.")
            
            # 2. Redirigir correctamente
            # Usar el namespace 'transporte' para resolver la URL
            return redirect('transporte:viaje_detalle', viaje_id=viaje.id) 
            
        # Si el formulario no es válido, volvemos a renderizar con errores
        mensajes = viaje.mensajes.all().order_by('timestamp')
        context = {
            'viaje': viaje,
            'mensajes': mensajes,
            'mensaje_form': form 
        }
        return render(request, self.template_name, context)


# ----------------------------------------------------------------------
# 4. Vistas de Administración
# ----------------------------------------------------------------------

class AdminAprobacionVehiculosView(AdminRequiredMixin, View):
    """Muestra una lista de vehículos pendientes de aprobación."""
    template_name = 'transporte/admin_vehiculos_pendientes.html'

    def get(self, request):
        # Filtrar por aprobado=False
        vehiculos_pendientes = Vehiculo.objects.filter(aprobado=False).select_related('conductor')
        context = {
            'vehiculos_pendientes': vehiculos_pendientes
        }
        return render(request, self.template_name, context)

class AprobarVehiculoView(AdminRequiredMixin, View):
    """Cambia el estado de 'aprobado' a True para un vehículo."""

    @method_decorator(require_POST)
    def post(self, request, vehiculo_id):
        # Obtener vehículo que está pendiente de aprobación
        vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id, aprobado=False)
        
        vehiculo.aprobado = True
        vehiculo.save()
        
        # Opcional: Marcar al conductor como disponible (si tu lógica lo requiere)
        conductor = vehiculo.conductor
        # La verificación de la licencia u otros requisitos debe estar en el modelo o un servicio
        if not conductor.disponible: 
            conductor.disponible = True
            conductor.save()
            messages.info(request, f"Conductor {conductor.username} marcado como DISPONIBLE.")

        messages.success(request, f"Vehículo {vehiculo.placa} aprobado con éxito.")
        return redirect('admin_aprobacion_vehiculos') # Redirige a la lista


# transporte/views.py (Solo las vistas de API - Añade esto al archivo)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import (
    VehiculoSerializer, 
    ViajeSerializer, 
    SolicitudAsistenciaSerializer, 
    MensajeViajeSerializer
)
from .models import (
    Vehiculo, 
    Viaje, 
    SolicitudAsistencia, 
    MensajeViaje
)
from .permissions import IsOwnerOrAdmin # Asume que crearás permisos para esto

# --- 1. API para Vehículos ---
class VehiculoViewSet(viewsets.ModelViewSet):
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticated]
    queryset = Vehiculo.objects.all()

    # Asegura que solo el conductor vea/modifique sus vehículos
    def get_queryset(self):
        # El administrador puede ver todos, el conductor solo los suyos
        if self.request.user.is_staff:
            return Vehiculo.objects.all()
        return Vehiculo.objects.filter(conductor=self.request.user)
    
    # Asigna automáticamente el conductor al crear
    def perform_create(self, serializer):
        serializer.save(conductor=self.request.user)

# --- 2. API para Viajes ---
class ViajeViewSet(viewsets.ModelViewSet):
    serializer_class = ViajeSerializer
    # Usaremos una consulta compleja para que solo el cliente o conductor vean el viaje
    queryset = Viaje.objects.all() 
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Viaje.objects.all()
        # Filtrar viajes donde el usuario es el cliente O el conductor
        return Viaje.objects.filter(
            Q(cliente=user) | Q(conductor=user)
        ).distinct()

    # Asigna automáticamente el cliente al crear
    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

# --- 3. API para Mensajes de Chat ---
class MensajeViajeViewSet(viewsets.ModelViewSet):
    serializer_class = MensajeViajeSerializer
    permission_classes = [IsAuthenticated]
    queryset = MensajeViaje.objects.all()
    
    def get_queryset(self):
        # Mostrar solo los mensajes de los viajes a los que el usuario pertenece
        user = self.request.user
        if user.is_staff:
            return MensajeViaje.objects.all()
            
        return MensajeViaje.objects.filter(
            Q(viaje__cliente=user) | Q(viaje__conductor=user)
        ).distinct()
        
    # Asigna automáticamente el emisor al crear
    def perform_create(self, serializer):
        serializer.save(emisor=self.request.user)
        
# --- 4. API para Asistencia Vial ---
class SolicitudAsistenciaViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudAsistenciaSerializer
    queryset = SolicitudAsistencia.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SolicitudAsistencia.objects.all()
        # Filtrar asistencias donde el usuario es el cliente O el proveedor
        return SolicitudAsistencia.objects.filter(
            Q(cliente=user) | Q(proveedor=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)