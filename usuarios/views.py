# usuarios/views.pyy
from django.db.models import Q, Max, Prefetch # Se necesita Max y Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q # Importación necesaria para buscar salas de chat

from .forms import LoginForm, ClienteRegistroForm, ConductorRegistroForm
from .models import PerfilConductor, UsuarioPersonalizado, ChatRoom, Mensaje # Importamos los modelos de chat
from rest_framework import viewsets

from .serializers import ClienteSerializer, ConductorRegistroSerializer, UsuarioDetalleSerializer
from .models import UsuarioPersonalizado
from .permissions import IsOwnerOrAdmin # Requerido



# ----------------------------------------------------------------------
# 1. Vistas de Autenticación
# ----------------------------------------------------------------------

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Maneja el inicio de sesión de todos los tipos de usuarios."""
    if request.user.is_authenticated:
        return redirect('home')  # Redirige si ya está logueado

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido, {user.username}. Has iniciado sesión como {user.get_rol_display()}.")
                return redirect('home')
            else:
                messages.error(request, "Nombre de usuario o contraseña inválidos.")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    
    else:
        form = LoginForm()
        
    return render(request, 'usuarios/login.html', {'form': form})

@login_required
def logout_view(request):
    """Cierra la sesión del usuario actual."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('home')


# ----------------------------------------------------------------------
# 2. Vistas de Registro
# ----------------------------------------------------------------------

@require_http_methods(["GET", "POST"])
def registro_cliente_view(request):
    """Registra un nuevo usuario con el rol 'cliente'."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = 'cliente' # Asignación explícita del rol
            user.save()
            messages.success(request, "¡Cuenta de Cliente creada con éxito! Por favor, inicia sesión.")
            return redirect('login')
        else:
            messages.error(request, "Error en el registro. Por favor, revisa los datos.")
    else:
        form = ClienteRegistroForm()
        
    return render(request, 'usuarios/registro_cliente.html', {'form': form})

@require_http_methods(["GET", "POST"])
def registro_conductor_view(request):
    """Registra un nuevo usuario con el rol 'conductor' o 'repartidor_domicilios'."""
    
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = ConductorRegistroForm(request.POST)
        
        if form.is_valid():
            # 1. El save() del formulario ahora guarda el User con todos sus campos
            user = form.save()  
            
            # 2. Inicializar campos que necesitan ser definidos después de guardar:
            user.disponible = False # No disponible hasta aprobación
            user.is_active = False # Puede que quieras dejarlo inactivo hasta que el admin apruebe
            user.save(update_fields=['disponible', 'is_active']) # <--- Solo actualiza los campos modificados
            
            # 3. Crear el perfil adicional de conductor con la licencia
            PerfilConductor.objects.create(
                usuario=user,
                licencia=form.cleaned_data.get('licencia') # Usar .get() es más seguro
            )

            messages.success(request, f"¡Registro completado! Tu cuenta ('{user.get_rol_display()}') ha sido enviada para aprobación administrativa. Por favor, inicia sesión.")
            return redirect('login')
        else:
            # LÍNEA DE DEPURACIÓN CRÍTICA: Muestra los errores en la terminal
            print("--- ERRORES DEL FORMULARIO ---")
            print(form.errors)  
            print("-----------------------------")
            # Si falla: El mensaje genérico se envía, y el HTML muestra los errores específicos.
            messages.error(request, "Error en el registro de proveedor. Por favor, revisa los datos marcados.")
    else:
        form = ConductorRegistroForm()
        
    return render(request, 'usuarios/registro_conductor.html', {'form': form})

# ----------------------------------------------------------------------
# 4. Vistas de Chat (NUEVO)
# ----------------------------------------------------------------------
@login_required
def chat_list_view(request):
    """
    Muestra la lista de salas de chat activas donde participa el usuario logueado.
    Ordena las salas por la fecha del último mensaje (timestamp).
    """
    user = request.user
    
    # 1. Encontrar todas las salas donde el usuario es participante
    chats_del_usuario = ChatRoom.objects.filter(participantes=user)
    
    # 2. Anotar la fecha del último mensaje en cada sala (usando 'timestamp')
    # ¡CORRECCIÓN CLAVE AQUÍ! Usamos 'timestamp' en lugar de 'fecha_envio'.
    chats_con_fecha = chats_del_usuario.annotate(
        ultimo_mensaje_fecha=Max('mensajes__timestamp')
    )
    
    # 3. Ordenar por la fecha del último mensaje (descendente)
    chats_ordenados = chats_con_fecha.exclude(
        ultimo_mensaje_fecha__isnull=True
    ).order_by('-ultimo_mensaje_fecha')
    
    # 4. Obtener el otro participante y el último mensaje para mostrar en el template
    lista_conversaciones = []
    
    for chat_room in chats_ordenados:
        otro_participante = chat_room.participantes.exclude(pk=user.pk).first()
        
        try:
            # Obtener el último mensaje usando el campo 'timestamp'
            ultimo_mensaje = chat_room.mensajes.latest('timestamp') 
        except Mensaje.DoesNotExist:
            ultimo_mensaje = None 

        if otro_participante:
            lista_conversaciones.append({
                'room': chat_room,
                'otro_participante': otro_participante,
                'ultimo_mensaje': ultimo_mensaje,
                'room_name_js': chat_room.room_name,
            })

    context = {
        'lista_conversaciones': lista_conversaciones,
    }
    return render(request, 'usuarios/chat_inbox.html', context)


@login_required
def chat_room_view(request, user_id):
    user = request.user
    # El usuario objetivo es el otro participante
    usuario_objetivo = UsuarioPersonalizado.objects.get(pk=user_id) 

    # 1. GENERACIÓN DEL NOMBRE DE LA SALA (ALFABÉTICO)
    # Esto asegura que el nombre de la sala sea único e independiente de quién la inició.
    participantes_ids = sorted([user.pk, usuario_objetivo.pk])
    room_name = f'chat_{participantes_ids[0]}_{participantes_ids[1]}' 

    # 2. OBTENER O CREAR la sala de chat
    chat_room, created = ChatRoom.objects.get_or_create(
        room_name=room_name
    )
    
    # 3. ASEGURAR QUE AMBOS USUARIOS ESTÉN EN LA RELACIÓN M2M
    if created or not chat_room.participantes.filter(pk=user.pk).exists():
        chat_room.participantes.add(user, usuario_objetivo)
    
    # 4. Obtener historial (usando el campo 'timestamp')
    historial = Mensaje.objects.filter(room=chat_room).order_by('timestamp') 

    context = {
        'room_name_js': room_name, # <-- CRÍTICO para el WebSocket
        'usuario_objetivo': usuario_objetivo,
        'historial': historial,
    }
    return render(request, 'usuarios/chat_room.html', context)



# usuarios/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Mensaje # Asegúrate de importar tus modelos

# Se asume que la ruta es 'chat/<int:room_id>/'

@login_required
def room(request, room_id):
    
    # 1. Obtener la Sala de Chat o lanzar 404
    # Usamos get_object_or_404 para asegurarnos de que la sala exista.
    chat_room = get_object_or_404(ChatRoom, pk=room_id)
    
    # 2. Obtener los últimos mensajes de esa sala
    # Usamos .select_related('autor') para optimizar la consulta de usuarios
    messages = Mensaje.objects.filter(room=chat_room).select_related('autor').order_by('fecha_envio')[:50]
    
    # 3. Preparar el Contexto
    context = {
        # CRÍTICO: Aquí pasamos el nombre real de la sala.
        'room_name': chat_room.room_name, 
        'messages': messages,
        # Puedes añadir otros datos relevantes, como el ID de la sala:
        'room_id': room_id,
    }
    
    return render(request, 'chat_room.html', context)




from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import serializers
from .models import UsuarioPersonalizado, PerfilConductor




from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
# 🚩 Importación de serializadores después de moverlos a serializers.py
from .serializers import ClienteSerializer, ConductorRegistroSerializer, UsuarioDetalleSerializer
from .models import UsuarioPersonalizado
from .permissions import IsOwnerOrAdmin # Requerido

from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado para permitir:
    1. Acceso de lectura (GET, HEAD, OPTIONS) a todos los autenticados.
    2. Acceso de escritura (PUT, PATCH, DELETE) solo al dueño o al admin.
    """
    
    # Permiso a nivel de vista (listado o creación)
    def has_permission(self, request, view):
        # Todos los usuarios autenticados pueden usar la vista
        return request.user.is_authenticated

    # Permiso a nivel de objeto (detalle, actualización)
    def has_object_permission(self, request, view, obj):
        # Permitir métodos de lectura (GET, HEAD, OPTIONS) para todos
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permitir métodos de escritura (PUT, PATCH, DELETE) si:
        # 1. El usuario es administrador (is_staff)
        if request.user.is_staff:
            return True
            
        # 2. El usuario es el dueño del objeto
        # Asume que 'obj' es una instancia de UsuarioPersonalizado.
        return obj.pk == request.user.pk

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Viewset que gestiona todas las operaciones del modelo UsuarioPersonalizado.
    Utiliza un serializador dinámico según la acción.
    """
    queryset = UsuarioPersonalizado.objects.all().exclude(rol='administrador')
    permission_classes = [IsOwnerOrAdmin] # Ya no hay error de NameError
    
    # Selecciona el serializador basado en la acción
    def get_serializer_class(self):
        if self.action == 'create':
            # POST sin acción custom (Registro de Cliente Simple)
            return ClienteSerializer 
        
        if self.action == 'registrar_conductor':
            # POST a /usuarios/registrar_conductor/ (Registro Anidado)
            return ConductorRegistroSerializer
            
        # GET, PUT, PATCH, DELETE: Usar el serializador seguro y completo
        return UsuarioDetalleSerializer
        
    # Acción custom para el registro anidado
    @action(detail=False, methods=['post'])
    def registrar_conductor(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)