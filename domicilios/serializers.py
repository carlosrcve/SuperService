# domicilios/serializers.py
from rest_framework import serializers

from .models import Comercio, Pedido, ItemPedido

# --- 1. Detalle del Pedido (Artículos) ---
class ItemPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        # CORRECCIÓN: Usa el nombre del modelo que sí existe
        model = ItemPedido 
        fields = ['id', 'producto', 'cantidad', 'precio_unitario'] # Nota: Usé 'producto' no 'producto_nombre' ya que es un FK
        # El pedido al que pertenece se maneja en la vista de creación

# ... (El resto del código se ajusta a continuación)

# --- 3. Serializador del Pedido (Incluye los detalles) ---
class PedidoSerializer(serializers.ModelSerializer):
    # Ajusta el nombre del campo anidado y usa el nuevo serializador
    items = ItemPedidoSerializer(many=True, read_only=True)
    
    # ... (otros campos)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente', 'cliente_username', 'repartidor', 'repartidor_username', 
            'comercio', 'comercio_nombre', 'direccion_entrega', 'total_final', 
            'estado', 'creado_en', 'items' # <-- Usa el nombre del related_name del modelo Pedido
        ]
        read_only_fields = ['repartidor', 'estado', 'total_final']


# --- 2. Serializador de Comercio (Tiendas) ---
class ComercioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comercio
        fields = ['id', 'nombre', 'direccion', 'telefono', 'tipo_comida', 'abierto']
        read_only_fields = ['abierto']

# --- 3. Serializador del Pedido (Incluye los detalles) ---
class PedidoSerializer(serializers.ModelSerializer):
    # Usa el serializador anterior para anidar los detalles
    articulos = ItemPedidoSerializer(many=True, read_only=True)
    
    # Campos de solo lectura para mejor contexto en la API
    cliente_username = serializers.ReadOnlyField(source='cliente.username')
    repartidor_username = serializers.ReadOnlyField(source='repartidor.username')
    comercio_nombre = serializers.ReadOnlyField(source='comercio.nombre')

    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente', 'cliente_username', 'repartidor', 'repartidor_username', 
            'comercio', 'comercio_nombre', 'direccion_entrega', 'total_final', 
            'estado', 'creado_en', 'articulos' # El campo anidado
        ]
        read_only_fields = ['repartidor', 'estado', 'total_final']