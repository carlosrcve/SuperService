# domicilios/permissions.py

from rest_framework import permissions

# --- Permisos de Comercio (Todos pueden ver, solo Admins pueden modificar) ---

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite el acceso de lectura (GET, HEAD, OPTIONS) a cualquier usuario.
    Permite el acceso de escritura (POST, PUT, DELETE) solo a administradores.
    """
    def has_permission(self, request, view):
        # Permiso de lectura para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permiso de escritura solo para administradores
        return request.user.rol == 'administrador'


# --- Permisos de Pedido (Reglas de Negocio Complejas) ---

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite acceso total si el usuario es el cliente del pedido, 
    el repartidor asignado, o un administrador.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # 1. Permiso al Administrador
        if user.rol == 'administrador':
            return True

        # 2. Permiso al Cliente (Owner)
        if obj.cliente == user:
            # Los clientes pueden ver el pedido, pero solo pueden cancelarlo si está pendiente
            if request.method in permissions.SAFE_METHODS or (request.method == 'PATCH' and obj.estado == 'pendiente'):
                return True
        
        # 3. Permiso al Repartidor Asignado
        if obj.repartidor == user:
            # Los repartidores pueden verlo y actualizar su estado (en_ruta, entregado)
            if request.method in permissions.SAFE_METHODS or request.method in ['PUT', 'PATCH']:
                return True
                
        return False