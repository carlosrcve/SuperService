# transporte/models.py
from django.db import models
from django.conf import settings # 🟢 ¡CRÍTICO: IMPORTAR SETTINGS AQUÍ!
from usuarios.models import UsuarioPersonalizado # Importar el modelo de usuario personalizado

# ----------------------------------------------------------------------
# 1. Gestión de Vehículos (Usados para Viajes, Envíos y Asistencia)
# ----------------------------------------------------------------------

from django.db import models
from usuarios.models import UsuarioPersonalizado # Asume esta importación

class Vehiculo(models.Model):
    """
    Representa un vehículo registrado por un conductor/repartidor.
    """
    TIPO_CHOICES = (
        ('auto', 'Automóvil (Viajes)'),
        ('moto', 'Motocicleta (Viajes y Envíos)'),
        ('bus', 'Autobús (Rutas Compartidas)'),
        ('camioneta', 'Camioneta (Asistencia Vial/Envío Grande)'),
    )
    
    conductor = models.ForeignKey(
        UsuarioPersonalizado, 
        on_delete=models.CASCADE, 
        # Restricción de roles a nivel de BD y admin
        limit_choices_to={'rol__in': ['conductor', 'repartidor_domicilios']}, 
        related_name='vehiculos'
    )
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    modelo = models.CharField(max_length=50)
    placa = models.CharField(max_length=10, unique=True)
    color = models.CharField(max_length=30, blank=True)
    
    # Indica si el vehículo ha sido aprobado por la administración
    aprobado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    def __str__(self):
        return f"{self.placa} - {self.modelo} ({self.get_tipo_display()})"

# ----------------------------------------------------------------------
# 2. Gestión de Viajes Solicitados
# ----------------------------------------------------------------------

class Viaje(models.Model):
    """
    Representa una solicitud de viaje de un cliente.
    """
    
    # --- Choices ---
    ESTADO_CHOICES = (
        ('solicitado', 'Solicitado'),
        ('aceptado', 'Aceptado por Conductor'),
        ('en_ruta_origen', 'En Ruta al Origen'),
        ('en_curso', 'En Curso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    )

    TIPO_SERVICIO_CHOICES = ( # 🟢 Nuevo: Choices para el tipo de servicio
        ('economy', 'Economy (Auto Estándar)'), 
        ('premium', 'Premium (Auto de Lujo)'), 
        ('moto', 'Moto/Taxi (Rápido y Económico)'),
    )

    # --- Relaciones ---
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Usar la configuración de Django
        on_delete=models.SET_NULL, 
        null=True, 
        # limit_choices_to={'rol': 'cliente'}, # Funciona si usas un ProxyManager, sino puede ser complejo
        related_name='viajes_solicitados'
    )
    conductor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        # limit_choices_to={'rol': 'conductor'},
        related_name='viajes_realizados'
    )
    # vehiculo_usado: Asegúrate de que la clase Vehiculo esté importada o definida
    vehiculo_usado = models.ForeignKey('Vehiculo', on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- Coordenadas y Ubicación (CRÍTICO para la Vista) ---
    # Sugerencia: Permitir Null/Blank si la vista falla, pero idealmente deben ser requeridos
    origen_lat = models.DecimalField(max_digits=9, decimal_places=6) 
    origen_lon = models.DecimalField(max_digits=9, decimal_places=6)
    destino_lat = models.DecimalField(max_digits=9, decimal_places=6)
    destino_lon = models.DecimalField(max_digits=9, decimal_places=6)
    
    # 🟢 CAMPOS FALTANTES QUE CAUSARON EL FIELDERROR:
    tipo_servicio = models.CharField(
        max_length=50, 
        choices=TIPO_SERVICIO_CHOICES, 
        default='economy',
        verbose_name="Tipo de Vehículo/Servicio Requerido"
    )
    
    notas_conductor = models.TextField(
        blank=True, 
        null=True,  
        verbose_name="Notas para el Conductor"
    )
    
    # --- Campos de Nombre de Dirección ---
    nombre_origen = models.CharField(max_length=255, blank=True, null=True)
    nombre_destino = models.CharField(max_length=255, blank=True, null=True)

    # --- Estado y Finanzas ---
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='solicitado')
    tarifa_estimada = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    tarifa_final = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # --- Tiempos ---
    creado_en = models.DateTimeField(auto_now_add=True)
    iniciado_en = models.DateTimeField(null=True, blank=True)
    finalizado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Viaje"
        verbose_name_plural = "Viajes"
        # Opcional: Para ordenar en la administración por la fecha de solicitud
        ordering = ['-creado_en'] 
    
    def __str__(self):
        return f"Viaje #{self.id} de {self.cliente.username} - {self.get_estado_display()}"
# ----------------------------------------------------------------------
# 3. Gestión de Asistencia Vial (Servicio Relacionado)
# ----------------------------------------------------------------------

class SolicitudAsistencia(models.Model):
    """
    Representa una solicitud de asistencia vial (grúa, cambio de llanta, etc.).
    """
    TIPO_ASISTENCIA_CHOICES = (
        ('grua', 'Servicio de Grúa'),
        ('llanta', 'Cambio de Llanta'),
        ('gasolina', 'Suministro de Gasolina'),
        ('bateria', 'Recarga de Batería'),
    )

    cliente = models.ForeignKey(
        UsuarioPersonalizado, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='asistencias_solicitadas'
    )
    tipo_asistencia = models.CharField(max_length=20, choices=TIPO_ASISTENCIA_CHOICES)
    
    # El conductor que proporciona la asistencia (puede ser un conductor especializado o uno de los existentes)
    proveedor = models.ForeignKey(
        UsuarioPersonalizado, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='asistencias_brindadas'
    )
    
    # Ubicación del incidente
    ubicacion_lat = models.DecimalField(max_digits=9, decimal_places=6)
    ubicacion_lon = models.DecimalField(max_digits=9, decimal_places=6)
    descripcion = models.TextField(blank=True)

    estado = models.CharField(max_length=20, choices=Viaje.ESTADO_CHOICES, default='solicitado') # Reutilizamos los estados de Viaje
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Asistencia Vial #{self.id} - {self.get_tipo_asistencia_display()}"



# transporte/models.py

from django.conf import settings
from django.db import models

# ... (otras clases de modelos) ...

class MensajeViaje(models.Model):
    """Modelo para mensajes de chat asociados a un Viaje."""
    viaje = models.ForeignKey(
        'Viaje', 
        on_delete=models.CASCADE, 
        related_name='mensajes' # Usaremos viaje.mensajes.all()
    )
    emisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Mensaje de Viaje"
        verbose_name_plural = "Mensajes de Viaje"

    def __str__(self):
        return f'Mensaje de {self.emisor.username} en Viaje #{self.viaje.id}'