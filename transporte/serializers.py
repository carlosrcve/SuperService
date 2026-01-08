# transporte/serializers.py
from rest_framework import serializers
from .models import (
    Vehiculo, 
    Viaje, 
    SolicitudAsistencia, 
    MensajeViaje
)

# --- 1. Serializador de Vehículo (FALTABA ESTE) ---
class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'

# --- 2. Serializador de Viaje (CORREGIDO PARA COORDINADAS Y APP) ---
class ViajeSerializer(serializers.ModelSerializer):
    cliente_username = serializers.ReadOnlyField(source='cliente.username')
    
    # Mapeo: 'origen' es lo que manda la App, 'nombre_origen' es lo que está en tu models.py
    origen = serializers.CharField(source='nombre_origen')
    destino = serializers.CharField(source='nombre_destino')
    monto = serializers.DecimalField(source='tarifa_estimada', max_digits=10, decimal_places=2)

    class Meta:
        model = Viaje
        fields = [
            'id', 'cliente', 'cliente_username', 'origen', 'destino', 
            'monto', 'estado', 'origen_lat', 'origen_lon', 
            'destino_lat', 'destino_lon'
        ]

# --- 3. Serializador de Mensajes ---
class MensajeViajeSerializer(serializers.ModelSerializer):
    emisor_username = serializers.ReadOnlyField(source='emisor.username')

    class Meta:
        model = MensajeViaje
        fields = ['id', 'viaje', 'emisor', 'emisor_username', 'contenido', 'timestamp']
        read_only_fields = ['emisor', 'timestamp']

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