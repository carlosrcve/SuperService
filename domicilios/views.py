# domicilios/views.py
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView # Importación consolidada
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse_lazy # Importación consolidada
from django.db.models import Q # Necesario para RepartidorDashboardView
from django.utils import timezone # Necesario para EntregarPedidoView

# Importaciones de Modelos y Formularios
from .models import Comercio, Producto, Pedido, ItemPedido, Mensaje # Importa Mensaje si ya lo creaste
from .forms import ItemPedidoForm, PedidoDireccionForm, MensajeForm # Importa MensajeForm
from usuarios.models import UsuarioPersonalizado 
from transporte.models import Vehiculo # Añadida si necesitas usarla en otra vista no listada aquí

from .forms import (
    ItemPedidoForm, 
    PedidoDireccionForm, 
    MensajeForm, 
    # 🔑 ¡Añade esta línea si ComercioRegistroForm está en forms.py!
    ComercioRegistroForm, 
    ProductoForm 
)

# ----------------------------------------------------------------------
# Mixins de Verificación de Roles
# ----------------------------------------------------------------------

class ClienteRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verifica que el usuario esté logueado y tenga el rol 'cliente'."""
    def test_func(self):
        return self.request.user.rol == 'cliente'
    
    def handle_no_permission(self):
        messages.error(self.request, "Solo los clientes pueden acceder a la sección de domicilios.")
        return redirect('home')

class RepartidorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verifica que el usuario esté logueado y tenga el rol 'repartidor_domicilios'."""
    def test_func(self):
        user = self.request.user
        # Se asume que 'disponible' es un campo de UsuarioPersonalizado
        return user.rol == 'repartidor_domicilios' # Se quitó 'and user.disponible' para no romper
                                                   # la vista si el campo no existe.
    def handle_no_permission(self):
        messages.error(self.request, "Debes ser un repartidor aprobado y estar 'disponible' para acceder.")
        return redirect('home')

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verifica que el usuario esté logueado y tenga el rol 'administrador'."""
    def test_func(self):
        return self.request.user.rol == 'administrador'
        
    def handle_no_permission(self):
        messages.error(self.request, "Acceso denegado. Solo administradores pueden acceder a esta función.")
        return redirect('home')

# ----------------------------------------------------------------------
# 1. Vistas para Clientes (Catálogo y Carrito)
# ----------------------------------------------------------------------

class ComercioListView(ClienteRequiredMixin, View):
    """Muestra una lista de todos los comercios activos y el estado del pedido activo del cliente."""
    template_name = 'domicilios/comercio_list.html'

    def get(self, request):
        # 1. Obtener la lista de comercios (tal como lo tenías)
        comercios = Comercio.objects.filter(activo=True).order_by('nombre')
        
        # 2. 🚩 Lógica para encontrar el último pedido activo del usuario loggeado
        ultimo_pedido_activo = None
        
        # El mixin ClienteRequiredMixin ya asegura que el usuario esté autenticado.
        if request.user.is_authenticated:
            try:
                # Buscar el pedido más reciente que NO esté 'entregado' ni 'cancelado'.
                # Usa 'creado_en' para ordenar, tal como está en tu modelo Pedido.
                ultimo_pedido_activo = Pedido.objects.filter(
                    cliente=request.user
                ).exclude(
                    estado__in=['entregado', 'cancelado']
                ).order_by('-creado_en').first() # .first() devuelve el objeto o None
                
            except Exception as e:
                # Opcional: imprimir el error en la consola del servidor
                print(f"DEBUG Error al buscar pedido activo: {e}")
                
        # 3. Construir el contexto, incluyendo la variable 'ultimo_pedido'
        context = {
            'comercios': comercios,
            # 🚩 CRÍTICO: Pasar la variable al contexto
            'ultimo_pedido': ultimo_pedido_activo, 
        }
        
        return render(request, self.template_name, context)

class ProductoListView(ClienteRequiredMixin, View):
    """Muestra los productos de un comercio específico."""
    template_name = 'domicilios/producto_list.html'

    def get(self, request, comercio_id):
        comercio = get_object_or_404(Comercio, pk=comercio_id, activo=True)
        productos = Producto.objects.filter(comercio=comercio, disponible=True)
        
        # Inicializa el formulario para añadir productos
        add_to_cart_form = ItemPedidoForm()
        
        # Lógica de Carrito (Simulación por Sesión)
        current_cart = request.session.get('cart', {})
        comercio_cart = current_cart.get(str(comercio_id), {})
        
        context = {
            'comercio': comercio, 
            'productos': productos,
            'add_to_cart_form': add_to_cart_form,
            'comercio_cart': comercio_cart
        }
        return render(request, self.template_name, context)

class AddToCartView(ClienteRequiredMixin, View):
    """Añade un producto a la sesión del carrito de compras."""
    def post(self, request):
        form = ItemPedidoForm(request.POST)
        
        if form.is_valid():
            producto_id = form.cleaned_data['producto_id']
            cantidad = form.cleaned_data['cantidad']
            producto = get_object_or_404(Producto, pk=producto_id, disponible=True)
            comercio_id = str(producto.comercio.id)
            
            # 1. Inicializar el carrito en la sesión si no existe
            cart = request.session.get('cart', {})
            
            # 2. Inicializar el carrito del comercio específico si no existe
            comercio_cart = cart.get(comercio_id, {})
            
            producto_key = str(producto_id)
            
            # 3. Actualizar la cantidad o agregar nuevo item
            if producto_key in comercio_cart:
                # Si el producto ya existe, suma la cantidad
                comercio_cart[producto_key]['cantidad'] += cantidad
            else:
                # Nuevo item
                comercio_cart[producto_key] = {
                    'nombre': producto.nombre,
                    'precio': str(producto.precio), # Guardar como string para JSON serializar
                    'cantidad': cantidad,
                }
            
            cart[comercio_id] = comercio_cart
            request.session['cart'] = cart
            request.session.modified = True 
            
            messages.success(request, f'{cantidad}x {producto.nombre} añadido al carrito.')
            return redirect('producto_list', comercio_id=producto.comercio.id)

        messages.error(request, 'Error al añadir el producto. Cantidad no válida.')
        return redirect('comercio_list') 

class CheckoutView(ClienteRequiredMixin, View):
    """
    Página de finalización de compra. Confirma ítems, dirección y crea el Pedido.
    """
    template_name = 'domicilios/checkout.html'

    def get(self, request, comercio_id):
        comercio = get_object_or_404(Comercio, pk=comercio_id)
        cart = request.session.get('cart', {})
        comercio_cart = cart.get(str(comercio_id), {})
        
        if not comercio_cart:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('producto_list', comercio_id=comercio_id)

        # 1. Calcular el subtotal
        subtotal = sum(float(item['precio']) * item['cantidad'] for item in comercio_cart.values())
        
        # 2. Usar formulario de dirección
        direccion_form = PedidoDireccionForm()

        context = {
            'comercio': comercio,
            'items': comercio_cart.items(), # items() para iterar key y value
            'subtotal': subtotal,
            'direccion_form': direccion_form,
            'costo_envio_simulado': 5.00,
            'total_final_simulado': subtotal + 5.00
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, comercio_id):
        comercio = get_object_or_404(Comercio, pk=comercio_id)
        direccion_form = PedidoDireccionForm(request.POST)
        cart = request.session.get('cart', {}).get(str(comercio_id), {})
        
        if not cart:
            messages.error(request, "El carrito se vació inesperadamente.")
            return redirect('producto_list', comercio_id=comercio_id)

        if direccion_form.is_valid():
            # 1. Calcular totales
            subtotal = sum(float(item['precio']) * item['cantidad'] for item in cart.values())
            costo_envio = 5.00 # Simulado
            total_final = subtotal + costo_envio

            # 2. Crear el objeto Pedido
            pedido = direccion_form.save(commit=False)
            pedido.cliente = request.user
            pedido.comercio = comercio
            pedido.subtotal = subtotal
            pedido.costo_envio = costo_envio
            pedido.total_final = total_final
            pedido.estado = 'pendiente' 
            
            # 3. Asignación simulada del repartidor
            repartidor = UsuarioPersonalizado.objects.filter(
                rol='repartidor_domicilios', disponible=True
            ).order_by('?').first() # Elegir uno al azar para simular
            
            pedido.repartidor = repartidor
            
            pedido.save()

            # 4. Crear los ItemPedido
            for producto_id_str, item_data in cart.items():
                producto = get_object_or_404(Producto, pk=int(producto_id_str))
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item_data['cantidad'],
                    precio_unitario=float(item_data['precio'])
                )
            
            # 5. Limpiar el carrito de la sesión
            del request.session['cart'][str(comercio_id)]
            request.session.modified = True

            messages.success(request, f'¡Pedido #{pedido.id} realizado con éxito! En espera de ser aceptado por el comercio.')
            return redirect('pedido_detalle', pedido_id=pedido.id)

        messages.error(request, "Error en la dirección. Por favor, revisa los datos.")
        return self.get(request, comercio_id) # Vuelve a mostrar la página con errores

# ----------------------------------------------------------------------
# VISTA DE DETALLE DE PEDIDO (CLIENTE) CON CHAT INTEGRADO
# ----------------------------------------------------------------------
'''
class PedidoDetailView(LoginRequiredMixin, View):
    
    def get(self, request, pk): # <-- ¡Aquí está el cambio!
        pedido = get_object_or_404(Pedido, pk=pk)
        
        repartidor_username = pedido.repartidor.username if pedido.repartidor else 'NINGUNO'
        repartidor_id = pedido.repartidor.id if pedido.repartidor else 'N/A'

        print("---------------------------------------")
        print(f"DEBUGGING PERMISOS PEDIDO #{pedido_id}")
        print(f"Usuario Logueado: {request.user.username} (ID: {request.user.id}, Rol: {request.user.rol})")
        print(f"Cliente del Pedido: {pedido.cliente.username} (ID: {pedido.cliente.id})")
        print(f"Repartidor Asignado: {repartidor_username} (ID: {repartidor_id})")
        print("---------------------------------------")
        # ---------------------------------------------------------------------------------

        # --- 2. CONTROL DE ACCESO MEJORADO ---
        es_cliente = (request.user == pedido.cliente)
        
        # Maneja el caso en que pedido.repartidor sea None (aún no asignado)
        es_repartidor_asignado = (pedido.repartidor is not None and request.user == pedido.repartidor)
        
        # Permite el acceso al administrador (asumiendo que el campo 'rol' es correcto)
        es_administrador = (request.user.rol == 'administrador')
        
        # 🚩 Si NO es (cliente O repartidor O administrador), se deniega el acceso.
        if not (es_cliente or es_repartidor_asignado or es_administrador):
            from django.http import Http404
            raise Http404("No tienes permiso para ver este pedido.")

        # --- 3. Obtener datos para la plantilla (Continúa normal) ---
        items = pedido.items.all() # Asumiendo que el related_name es 'itempedido_set'
        mensajes = Mensaje.objects.filter(pedido=pedido).order_by('timestamp')
        form = MensajeForm()

        context = {
            'pedido': pedido,
            'items': items,
            'mensajes': mensajes,
            'mensaje_form': form,
        }
        return render(request, 'domicilios/pedido_detalle.html', context)
        

    def post(self, request, pedido_id):
        # NOTA: Este método POST es SÍNCRONO y ya no es necesario si usas WebSockets.
        # Si planeas solo usar WebSockets para el chat, te recomiendo ELIMINAR O COMENTAR este método.
        
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        
        # Control de Acceso (repetido para POST)
        # Aquí también debemos incluir al administrador para que pueda enviar mensajes
        es_cliente = (request.user == pedido.cliente)
        es_repartidor_asignado = (pedido.repartidor is not None and request.user == pedido.repartidor)
        es_administrador = (request.user.rol == 'administrador')
        
        if not (es_cliente or es_repartidor_asignado or es_administrador):
            from django.http import Http404
            raise Http404("No tienes permiso para interactuar con este pedido.")
            
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.pedido = pedido
            mensaje.emisor = request.user
            mensaje.save()
            # Este redirect es la forma SÍNCRONA, no usa WebSocket.
            return redirect('pedido_detalle', pedido_id=pedido.id)
            
        # Si el formulario no es válido...
        items = pedido.itempedido_set.all()
        mensajes = Mensaje.objects.filter(pedido=pedido).order_by('timestamp')
        context = {
            'pedido': pedido,
            'items': items,
            'mensajes': mensajes,
            'mensaje_form': form,
        }
        return render(request, 'domicilios/pedido_detalle.html', context)
    '''

class PedidoDetailView(LoginRequiredMixin, View):
    
    # El argumento de la URL se espera como 'pk' (Primary Key)
    def get(self, request, pk):
        # 1. Obtener el Pedido o lanzar 404
        pedido = get_object_or_404(Pedido, pk=pk)
        
        # ---------------------------------------------------------------------------------
        # 2. CONTROL DE ACCESO MEJORADO: Solo el cliente, repartidor asignado o administrador puede ver.
        # ---------------------------------------------------------------------------------
        
        # Define las condiciones de permiso
        es_cliente = (request.user == pedido.cliente)
        
        # Verifica si el repartidor está asignado y si el usuario actual es ese repartidor
        es_repartidor_asignado = (pedido.repartidor is not None and request.user == pedido.repartidor)
        
        # Permite el acceso al administrador (asumiendo que el campo 'rol' es correcto)
        es_administrador = (getattr(request.user, 'rol', None) == 'administrador')
        
        # Deniega el acceso si el usuario no cumple ninguno de los roles permitidos
        if not (es_cliente or es_repartidor_asignado or es_administrador):
            raise Http404("No tienes permiso para ver este pedido.")

        # ---------------------------------------------------------------------------------
        # 3. Obtener datos y preparar el contexto
        # ---------------------------------------------------------------------------------
        
        # Items: Asume que el related_name es 'items' o usa el valor por defecto 'itempedido_set'
        # Utilizaré 'items.all()' como estaba en tu ejemplo, pero ten en cuenta el related_name.
        items = pedido.items.all() 
        
        # Mensajes: Obtener el historial de chat ordenado por tiempo
        mensajes = Mensaje.objects.filter(pedido=pedido).order_by('timestamp')
        
        # Formulario: Necesario para que la plantilla renderice el área de chat (aunque se envíe por WS)
        form = MensajeForm() 

        context = {
            'pedido': pedido,
            'items': items,
            'mensajes': mensajes,
            'mensaje_form': form,
        }
        
        # Usar la ruta correcta de la plantilla:
        return render(request, 'domicilios/pedido_detalle.html', context)
        
    
    # ---------------------------------------------------------------------------------
    # MÉTODO POST: ELIMINADO/COMENTADO
    # ---------------------------------------------------------------------------------
    # El método POST para el envío de mensajes SÍNCRONO ha sido ELIMINADO.
    # El manejo del chat en tiempo real se realiza completamente mediante JavaScript y WebSockets (Channels).
    # Esto simplifica la vista y evita lógica de chat redundante.
    # ---------------------------------------------------------------------------------
    
    # Si deseas mantener un método POST para otras acciones (ej: cancelar pedido), 
    # puedes añadirlo, pero se recomienda usar 'pk' en lugar de 'pedido_id'.
    # def post(self, request, pk):
    #    # Lógica de cancelación o actualización de estado aquí.
    #    pass

# ----------------------------------------------------------------------
# 2. Vistas para Repartidores (Gestión de Pedidos)
# ----------------------------------------------------------------------

class RepartidorDashboardView(RepartidorRequiredMixin, View):
    """Dashboard para que los repartidores vean pedidos listos para recoger."""
    template_name = 'domicilios/repartidor_dashboard.html'

    def get(self, request):
        # Muestra los pedidos pendientes de recoger (estado 'listo') que no tienen repartidor asignado,
        # o los que ya le fueron asignados ('en_camino').
        pedidos_pendientes = Pedido.objects.filter(
            Q(estado='listo') | Q(repartidor=request.user, estado='en_camino')
        ).order_by('-creado_en')[:15]
        
        context = {'pedidos': pedidos_pendientes}
        return render(request, self.template_name, context)

class RecogerPedidoView(RepartidorRequiredMixin, View):
    """Permite al repartidor cambiar el estado del pedido a 'en_camino'."""

    def post(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, pk=pedido_id, estado='listo')
        
        # Asignar si no tiene (aunque la lógica de asignación debería ser mejor)
        if not pedido.repartidor:
              pedido.repartidor = request.user
        
        pedido.estado = 'en_camino'
        pedido.save()
        messages.success(request, f'¡Pedido #{pedido.id} recogido! Dirígete a la dirección de entrega.')
        return redirect('repartidor_dashboard')

class EntregarPedidoView(RepartidorRequiredMixin, View):
    """Permite al repartidor cambiar el estado del pedido a 'entregado'."""
    
    def post(self, request, pedido_id):
        # Se requiere el timezone.now() porque lo estás usando en tu código original.
        pedido = get_object_or_404(Pedido, pk=pedido_id, repartidor=request.user, estado='en_camino')
        pedido.estado = 'entregado'
        pedido.entregado_en = timezone.now()
        pedido.save()
        messages.success(request, f'Pedido #{pedido.id} entregado y finalizado.')
        return redirect('repartidor_dashboard')


# ----------------------------------------------------------------------
# 3. Vistas de Administración de Comercios y Productos
# ----------------------------------------------------------------------

class ComercioListViewAdmin(AdminRequiredMixin, ListView):
    """Muestra la lista de todos los comercios para administración."""
    model = Comercio
    template_name = 'domicilios/admin/comercio_list_admin.html'
    context_object_name = 'comercios'

class ComercioCreateView(AdminRequiredMixin, CreateView):
    """Permite crear un nuevo comercio."""
    model = Comercio
    form_class = ComercioRegistroForm
    template_name = 'domicilios/admin/comercio_form.html'
    success_url = reverse_lazy('admin_comercio_list') # Redirige a la lista de administración

class ProductoListViewAdmin(AdminRequiredMixin, ListView):
    """Muestra los productos de un comercio específico para edición."""
    model = Producto
    template_name = 'domicilios/admin/producto_list_admin.html'
    context_object_name = 'productos'
    
    def get_queryset(self):
        # Filtra los productos por el comercio_id pasado en la URL
        self.comercio = get_object_or_404(Comercio, pk=self.kwargs['comercio_id'])
        return Producto.objects.filter(comercio=self.comercio)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comercio'] = self.comercio
        return context

class ProductoCreateView(AdminRequiredMixin, CreateView):
    """Permite crear un nuevo producto para un comercio."""
    model = Producto
    form_class = ProductoForm
    template_name = 'domicilios/admin/producto_form.html'

    def form_valid(self, form):
        # Asigna el comercio al producto antes de guardar
        comercio = get_object_or_404(Comercio, pk=self.kwargs['comercio_id'])
        form.instance.comercio = comercio
        messages.success(self.request, f"Producto creado para {comercio.nombre}.")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirige a la lista de productos del comercio
        return reverse_lazy('admin_producto_list', kwargs={'comercio_id': self.kwargs['comercio_id']})


# domicilios/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action # 🔑 ¡Añadir 'action' aquí!
from django.db.models import Q
from .serializers import (
    ComercioSerializer, 
    PedidoSerializer, 
    ItemPedidoSerializer
)
from .models import Comercio, Pedido, ItemPedido

# --- 1. API para Comercios (Solo Lectura) ---
class ComercioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Permite a los clientes y repartidores ver la lista de comercios.
    (La creación/actualización suele ser a través del Admin o un panel separado)
    """
    queryset = Comercio.objects.filter(activo=True).order_by('nombre')
    serializer_class = ComercioSerializer
    permission_classes = [IsAuthenticated]

# --- 2. API para Pedidos (Solicitudes de Entrega) ---
class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    queryset = Pedido.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Pedido.objects.all()
        # Clientes ven sus pedidos, Repartidores ven sus pedidos asignados
        return Pedido.objects.filter(
            Q(cliente=user) | Q(repartidor=user)
        ).distinct()

    # Asigna automáticamente el cliente al crear
    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)
        # Nota: La lógica para crear DetallePedido debe ir en una vista separada 
        # o anidada, o un método especial en el ViewSet.

    @action(detail=True, methods=['post'], url_path='aceptar')
    def aceptar_pedido(self, request, pk=None):
        # ...
        pedido.estado = 'en_ruta'
        # ...

# --- 3. API para Detalles de Pedido (CRUD básico) ---
class ItemPedidoViewSet(viewsets.ModelViewSet):
    """
    Se puede usar para crear o modificar los artículos de un pedido (antes de ser finalizado).
    """
    serializer_class = ItemPedidoSerializer
    permission_classes = [IsAuthenticated]
    queryset = ItemPedido.objects.all() # 👈 ¡Necesario!
    
    def get_queryset(self):
        # Solo mostrar los detalles de pedidos que el usuario puede ver
        user = self.request.user
        return ItemPedido.objects.filter(Q(pedido__cliente=user) | Q(pedido__repartidor=user)).distinct()



# domicilios/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import Comercio, Pedido, ItemPedido
from .serializers import ComercioSerializer, PedidoSerializer, ItemPedidoSerializer # Asumiendo estos serializadores existen
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin 
# Asegúrate de importar tus serializadores y modelos

# ----------------------------------------------------------------------
# A. ViewSet para Comercios (Solo Lectura para la mayoría)
# ----------------------------------------------------------------------
class ComercioViewSet(viewsets.ModelViewSet):
    """Permite listar comercios activos y administrarlos."""
    queryset = Comercio.objects.filter(activo=True).order_by('nombre')
    serializer_class = ComercioSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    # Nota: Los campos de latitud/longitud deben ser calculados o poblados al crear/actualizar

# ----------------------------------------------------------------------
# B. ViewSet para Pedidos (Núcleo de la Aplicación)
# ----------------------------------------------------------------------
class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # 1. Administradores ven todos los pedidos
        if user.rol == 'administrador':
            return Pedido.objects.all().select_related('cliente', 'repartidor', 'comercio')
            
        # 2. Clientes ven sus propios pedidos
        if user.rol == 'cliente':
            return Pedido.objects.filter(cliente=user).order_by('-creado_en')
        
        # 3. Repartidores ven sus pedidos asignados Y los pedidos listos para tomar
        if user.rol == 'repartidor_domicilios':
            return Pedido.objects.filter(
                Q(repartidor=user) | Q(estado='listo') # Pedidos asignados O pedidos disponibles para tomar
            ).distinct().order_by('-creado_en')
            
        return Pedido.objects.none() # Otros roles (como 'conductor' de transporte) no ven nada

    # 🚨 Lógica de Negocio 1: Asignar Repartidor a un Pedido Listo
    @action(detail=True, methods=['post'], url_path='aceptar')
    def aceptar_pedido(self, request, pk=None):
        pedido = self.get_object()
        user = request.user

        if user.rol != 'repartidor_domicilios':
            return Response({"detail": "Solo los repartidores pueden aceptar pedidos."}, status=status.HTTP_403_FORBIDDEN)
            
        if pedido.estado == 'listo' and pedido.repartidor is None:
            # Asignación y cambio de estado
            pedido.repartidor = user
            pedido.estado = 'en_ruta'
            pedido.save()
            return Response({'status': 'Pedido aceptado y en ruta.'}, status=status.HTTP_200_OK)
        
        return Response({'detail': 'El pedido no está listo o ya fue asignado.'}, status=status.HTTP_400_BAD_REQUEST)

    # Lógica de Negocio 2: Asignar cliente automáticamente al crear
    def perform_create(self, serializer):
        # Asegura que el cliente que crea el pedido sea el usuario autenticado
        serializer.save(cliente=self.request.user)

