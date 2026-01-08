# domicilios/serializers.py

# domicilios/serializers.py
from rest_framework import serializers
from .models import Comercio, Categoria, Producto, Pedido, ItemPedido

# 1. Categoría
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

# 2. Producto
class ProductoSerializer(serializers.ModelSerializer):
    comercio_nombre = serializers.ReadOnlyField(source='comercio.nombre')
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')

    class Meta:
        model = Producto
        fields = '__all__'

# 3. Comercio
class ComercioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comercio
        fields = '__all__'

# 4. Items (Detalle del pedido)
class ItemPedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    
    class Meta:
        model = ItemPedido
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario']

# 5. Pedido (Final y Corregido)
class PedidoSerializer(serializers.ModelSerializer):
    cliente_username = serializers.ReadOnlyField(source='cliente.username')
    comercio_nombre = serializers.ReadOnlyField(source='comercio.nombre')
    items = ItemPedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'
        read_only_fields = ['repartidor', 'estado', 'total_final', 'creado_en']