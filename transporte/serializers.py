# transporte/serializers.py
from rest_framework import serializers
from .models import (
    Vehiculo, 
    Viaje, 
    SolicitudAsistencia, 
    MensajeViaje
)

# --- 1. Serializador de Vehículo ---
class VehiculoSerializer(serializers.ModelSerializer):
    # conductor será un campo de solo lectura
    conductor = serializers.ReadOnlyField(source='conductor.username') 

    class Meta:
        model = Vehiculo
        fields = ['id', 'conductor', 'tipo', 'modelo', 'placa', 'aprobado']
        # La app móvil podría querer registrar el vehículo, pero no aprobarlo
        read_only_fields = ['aprobado'] 

# --- 2. Serializador de Viaje (CRÍTICO) ---
class ViajeSerializer(serializers.ModelSerializer):
    # Mostrar el nombre de usuario del cliente/conductor
    cliente_username = serializers.ReadOnlyField(source='cliente.username')
    conductor_username = serializers.ReadOnlyField(source='conductor.username')
    
    class Meta:
        model = Viaje
        fields = [
            'id', 'cliente', 'cliente_username', 'conductor', 'conductor_username', 
            'vehiculo_usado', 'tipo_servicio', 'notas_conductor', 'nombre_origen', 
            'nombre_destino', 'origen_lat', 'origen_lon', 'destino_lat', 
            'destino_lon', 'estado', 'tarifa_estimada', 'creado_en'
        ]
        # Campos que el cliente no puede modificar al crear la solicitud:
        read_only_fields = ['conductor', 'vehiculo_usado', 'estado', 'tarifa_estimada']

# --- 3. Serializador de Mensajes ---
class MensajeViajeSerializer(serializers.ModelSerializer):
    # Mostrar el nombre del emisor
    emisor_username = serializers.ReadOnlyField(source='emisor.username')

    class Meta:
        model = MensajeViaje
        fields = ['id', 'viaje', 'emisor', 'emisor_username', 'contenido', 'timestamp']
        read_only_fields = ['emisor', 'timestamp'] # El emisor se asigna automáticamente

# --- 4. Serializador de Asistencia Vial ---
class SolicitudAsistenciaSerializer(serializers.ModelSerializer):
    cliente_username = serializers.ReadOnlyField(source='cliente.username')
    proveedor_username = serializers.ReadOnlyField(source='proveedor.username')
    
    class Meta:
        model = SolicitudAsistencia
        fields = [
            'id', 'cliente', 'cliente_username', 'proveedor', 'proveedor_username', 
            'tipo_asistencia', 'ubicacion_lat', 'ubicacion_lon', 
            'descripcion', 'estado', 'creado_en'
        ]
        read_only_fields = ['proveedor', 'estado', 'creado_en']