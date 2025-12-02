# usuarios/permissions.py

from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado para permitir:
    1. Acceso de lectura (GET, HEAD, OPTIONS) a todos los autenticados.
    2. Acceso de escritura (PUT, PATCH, DELETE) solo al dueño o al admin.
    """
    
    # Permiso a nivel de vista
    def has_permission(self, request, view):
        return request.user.is_authenticated

    # Permiso a nivel de objeto
    def has_object_permission(self, request, view, obj):
        # Permitir métodos de lectura
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permitir métodos de escritura si es admin o dueño
        if request.user.is_staff:
            return True
            
        return obj.pk == request.user.pk