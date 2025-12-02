# usuarios/serializers.py

from rest_framework import serializers
from .models import UsuarioPersonalizado, PerfilConductor
from django.db import transaction

# ----------------------------------------------------------------------
# 1. Serializador de Perfil de Conductor
# ----------------------------------------------------------------------

class PerfilConductorSerializer(serializers.ModelSerializer):
    """
    Serializador para la información específica del conductor (licencia, rating, etc.).
    """
    class Meta:
        model = PerfilConductor
        # El campo 'usuario' se gestiona desde el Serializador padre
        fields = ['licencia', 'rating', 'cuenta_bancaria']
        read_only_fields = ['rating'] # El rating no es editable por el usuario
        
# ----------------------------------------------------------------------
# 2. Serializador de Usuario Personalizado (Cliente)
# ----------------------------------------------------------------------

class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializador para Clientes. Usa este para registrar nuevos Clientes.
    """
    # El campo 'password' solo es de escritura y no se muestra al leer
    password = serializers.CharField(write_only=True) 

    class Meta:
        model = UsuarioPersonalizado
        fields = ['id', 'username', 'email', 'password', 'rol', 'telefono']
        read_only_fields = ['rol', 'disponible']
        
    def create(self, validated_data):
        # Asegura que el rol sea 'cliente' al registrar
        validated_data['rol'] = 'cliente' 
        
        # Crea el usuario y hashea la contraseña
        user = UsuarioPersonalizado.objects.create_user(**validated_data)
        return user

# ----------------------------------------------------------------------
# 3. Serializador Anidado de Conductor/Repartidor (Registro Completo)
# ----------------------------------------------------------------------

class ConductorRegistroSerializer(serializers.ModelSerializer):
    """
    Serializador para registrar a un Conductor/Repartidor. 
    Incluye los datos del PerfilConductor de forma anidada.
    """
    # 🚨 Serializador Anidado: Usa el PerfilConductorSerializer aquí
    perfil_conductor = PerfilConductorSerializer(required=True)
    password = serializers.CharField(write_only=True)
    
    # Restricción: El usuario debe indicar su rol de servicio (conductor o repartidor)
    rol = serializers.ChoiceField(
        choices=[('conductor', 'Conductor de Viajes'), ('repartidor_domicilios', 'Repartidor de Domicilios')]
    )

    class Meta:
        model = UsuarioPersonalizado
        fields = ['id', 'username', 'email', 'password', 'rol', 'telefono', 'perfil_conductor']
        read_only_fields = ['disponible']

    # --- Lógica de Creación Anidada ---
    def create(self, validated_data):
        # Garantiza que ambas operaciones se completen o ninguna (Atomic Transaction)
        with transaction.atomic():
            # 1. Obtener los datos del PerfilConductor antes de crear el usuario
            perfil_data = validated_data.pop('perfil_conductor')
            
            # 2. Crear el UsuarioPersonalizado (Conductor/Repartidor)
            user = UsuarioPersonalizado.objects.create_user(**validated_data)
            
            # 3. Crear el PerfilConductor, relacionándolo con el nuevo usuario
            PerfilConductor.objects.create(usuario=user, **perfil_data)
            
            return user


# usuarios/serializers.py (CÓDIGO A AGREGAR AL FINAL)

# ----------------------------------------------------------------------
# 4. Serializador de Detalle y Actualización (Lectura/Escritura Parcial)
# ----------------------------------------------------------------------

class UsuarioDetalleSerializer(serializers.ModelSerializer):
    """
    Serializador de detalle y actualización. Utilizado para GET/PUT/PATCH 
    en el ViewSet. Permite actualizar campos clave como teléfono o disponibilidad.
    """
    # Usamos el Serializador de Conductor definido arriba (1.) para la vista de detalle
    perfil_conductor = PerfilConductorSerializer(read_only=True, required=False) 

    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'rol', 'telefono', 'disponible', 'perfil_conductor', 
            'latitud', 'longitud'
        ]
        # Hacemos todos los campos de solo lectura por defecto
        read_only_fields = fields 
    
    # --- Lógica de Actualización ---
    def update(self, instance, validated_data):
        # Permite actualizar solo campos específicos
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.disponible = validated_data.get('disponible', instance.disponible)
        instance.latitud = validated_data.get('latitud', instance.latitud)
        instance.longitud = validated_data.get('longitud', instance.longitud)
        
        instance.save()
        return instance