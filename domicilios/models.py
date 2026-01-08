# domicilios/models.py
from django.db import models
from usuarios.models import UsuarioPersonalizado # Importar el modelo de usuario
from transporte.models import Vehiculo

# ----------------------------------------------------------------------
# 1. Gestión de Comercios (Proveedores)
# ----------------------------------------------------------------------

class Comercio(models.Model):
    """
    Representa un restaurante, supermercado o farmacia en la plataforma.
    """
    TIPO_CHOICES = (
        ('restaurante', 'Restaurante'),
        ('supermercado', 'Supermercado'),
        ('farmacia', 'Farmacia'),
    )
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Dueño del comercio (opcional si es manejado por un solo administrador)
    propietario = models.ForeignKey(
        UsuarioPersonalizado, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='comercios_asociados'
    )
    
    # Ubicación del comercio para calcular distancias
    direccion = models.CharField(max_length=255)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    
    activo = models.BooleanField(default=True, help_text="Indica si el comercio está recibiendo pedidos.")

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class Producto(models.Model):
    """
    Representa un artículo que se puede comprar de un Comercio.
    """
    comercio = models.ForeignKey(Comercio, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    
    disponible = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} de {self.comercio.nombre}"

# ----------------------------------------------------------------------
# 2. Gestión de Pedidos
# ----------------------------------------------------------------------

class Pedido(models.Model):
    """
    Representa una solicitud de compra de un cliente a un comercio.
    """
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente de Aceptación'),
        ('preparando', 'En Preparación'),
        ('listo', 'Listo para Recoger'),
        ('en_camino', 'En Camino al Cliente'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    
    cliente = models.ForeignKey(
        UsuarioPersonalizado, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='pedidos_cliente'
    )
    repartidor = models.ForeignKey(
        UsuarioPersonalizado, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        limit_choices_to={'rol': 'repartidor_domicilios'}, # Solo repartidores
        related_name='pedidos_repartidor'
    )

    # 🔑 CORRECCIÓN: AGREGAR EL CAMPO VEHÍCULO USADO
    vehiculo_usado = models.ForeignKey(
        'transporte.Vehiculo',
        on_delete=models.SET_NULL,
        null=True, blank=True, # Puede ser nulo hasta que el repartidor lo asigne
        related_name='pedidos_asignados',
        verbose_name='Vehículo Usado en el Pedido'
    )

    comercio = models.ForeignKey(Comercio, on_delete=models.PROTECT) # PROTECT para no borrar pedidos si se elimina el comercio
    
    # Detalles de la entrega
    direccion_entrega = models.CharField(max_length=255)
    lat_entrega = models.DecimalField(max_digits=9, decimal_places=6)
    lon_entrega = models.DecimalField(max_digits=9, decimal_places=6)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    subtotal = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    costo_envio = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total_final = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    entregado_en = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} a {self.comercio.nombre}"

class ItemPedido(models.Model):
    """
    Artículos individuales dentro de un Pedido.
    """
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=6, decimal_places=2) # Precio al momento de la compra

    def subtotal_item(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"



# domicilios/models.py (Añadir al final del archivo)
# ... después de la clase ItemPedido ...

# ----------------------------------------------------------------------
# 3. Comunicación (Chat simple)
# ----------------------------------------------------------------------

class Mensaje(models.Model):
    """
    Representa un mensaje enviado entre el cliente y el repartidor
    asociado a un Pedido específico.
    """
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='mensajes',
        verbose_name='Pedido Asociado'
    )
    
    # Usuario que envía el mensaje (puede ser el cliente o el repartidor)

    emisor = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados',
        verbose_name='Emisor'


    )
    
    contenido = models.TextField(verbose_name='Contenido del Mensaje')
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha/Hora de Envío'
    )

    class Meta:
        verbose_name = "Mensaje de Pedido"
        verbose_name_plural = "Mensajes de Pedido"
        # Ordenamos los mensajes por la hora de envío para el historial del chat
        ordering = ['timestamp']

    def __str__(self):
        # Muestra un extracto del mensaje para fácil identificación
        return f"Mensaje de {self.emisor.username} en Pedido #{self.pedido.id}: {self.contenido[:30]}..."



class Categoria(models.Model):  # <--- ESTO ES LO QUE FALTA
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='categorias/', null=True, blank=True)

    def __str__(self):
        return self.nombre