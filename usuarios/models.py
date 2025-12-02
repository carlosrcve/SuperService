# usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Obtener el modelo de usuario personalizado (usado dentro del propio archivo)
# Se define localmente para evitar problemas de dependencia circular
# aunque la referencia real en FKs es UsuarioPersonalizado
Usuario = settings.AUTH_USER_MODEL 

# ----------------------------------------------------------------------
# 1. MODELO DE USUARIO PERSONALIZADO
# ----------------------------------------------------------------------

class UsuarioPersonalizado(AbstractUser):
    """
    Modelo de Usuario Personalizado que extiende AbstractUser de Django.
    Permite agregar campos específicos como el 'rol' para la plataforma.
    """
    
    # Definición de los roles posibles
    ROL_CHOICES = (
        ('cliente', 'Cliente'),
        ('conductor', 'Conductor de Viajes'),
        ('repartidor_domicilios', 'Repartidor de Domicilios'),
        ('administrador', 'Administrador'),
    )
    
    # Campos adicionales
    rol = models.CharField(max_length=30, choices=ROL_CHOICES, default='cliente')
    telefono = models.CharField(max_length=15, unique=True, blank=True, null=True)
    disponible = models.BooleanField(default=False) # Para conductores/repartidores

    def __str__(self):
        """Devuelve una representación legible del objeto."""
        nombre_completo = self.get_full_name() or self.username
        return f"{nombre_completo} ({self.get_rol_display()})"

# ----------------------------------------------------------------------
# 2. MODELO DE PERFIL DE CONDUCTOR
# ----------------------------------------------------------------------

class PerfilConductor(models.Model):
    """
    Modelo complementario para almacenar información específica de Conductores y Repartidores.
    """
    
    usuario = models.OneToOneField(UsuarioPersonalizado, on_delete=models.CASCADE, primary_key=True)
    
    licencia = models.CharField(max_length=50, unique=True, blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    cuenta_bancaria = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"


# ----------------------------------------------------------------------
# 3. MODELOS PARA EL CHAT P2P (CORREGIDOS)
# ----------------------------------------------------------------------

class ChatRoom(models.Model):
    """Representa una sala de chat entre dos o más usuarios."""
    
    # CRÍTICO: Usado en la vista chat_list_view para filtrar las salas
    participantes = models.ManyToManyField(UsuarioPersonalizado, related_name='chat_rooms')
    
    room_name = models.CharField(max_length=255, unique=True)
    timestamp_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_name

class Mensaje(models.Model):
    """Representa un mensaje enviado en una sala de chat."""
    
    # CRÍTICO: related_name='mensajes' permite la notación 'mensajes__timestamp'
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='mensajes')
    
    autor = models.ForeignKey(
        UsuarioPersonalizado, 
        on_delete=models.CASCADE, 
        related_name='mensajes_chat_enviados' 
    )
    
    contenido = models.TextField()
    
    # CRÍTICO: El nombre del campo es 'timestamp' (Usado en la vista y plantillas)
    timestamp = models.DateTimeField(auto_now_add=True) 

    class Meta:
        # Ordenación por defecto, asegura que el último mensaje es el más reciente
        ordering = ['timestamp'] 

    def __str__(self):
        return f"Mensaje de {self.autor.username} en {self.room.room_name}"