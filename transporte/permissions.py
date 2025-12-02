# transporte/permissions.py

from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado para Viajes y Solicitudes de Asistencia.
    Permite el acceso completo (R/W) al dueño del objeto (cliente o conductor/proveedor) o al administrador (is_staff).
    """
    
    # Permiso a nivel de vista (listado o creación)
    def has_permission(self, request, view):
        # Todos los usuarios autenticados pueden usar la API.
        return request.user.is_authenticated

    # Permiso a nivel de objeto (detalle, actualización, eliminación)
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # 1. Los administradores (is_staff) tienen acceso total.
        if user.is_staff:
            return True
        
        # 2. Permitir GET (lectura) a cualquier participante
        if request.method in permissions.SAFE_METHODS:
            # Para Viaje: es cliente o conductor.
            if hasattr(obj, 'cliente') and obj.cliente == user:
                return True
            if hasattr(obj, 'conductor') and obj.conductor == user:
                return True
            # Para SolicitudAsistencia: es cliente o proveedor.
            if hasattr(obj, 'proveedor') and obj.proveedor == user:
                return True
            
        # 3. Para métodos de escritura (PUT, PATCH, DELETE): 
        # Solo permitir al cliente original (y solo si el estado lo permite, lo cual se maneja en el serializer/viewset).
        # Generalmente, solo el cliente o el admin pueden cancelar/modificar un viaje.
        # Simplificamos: solo el cliente puede modificar su propia solicitud.
        if request.method in ['PUT', 'PATCH', 'DELETE']:
             if hasattr(obj, 'cliente') and obj.cliente == user:
                 return True
        
        return False