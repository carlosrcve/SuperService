# domicilios/forms.py
from django import forms
from .models import Comercio, Producto, Pedido, ItemPedido
from transporte.models import Vehiculo  # Importación del modelo de vehículo
from usuarios.models import UsuarioPersonalizado # Necesario si lo usas para filtrar

# ----------------------------------------------------------------------
# 1. Formularios de Gestión (Comercios/Administradores)
# ----------------------------------------------------------------------

class ComercioRegistroForm(forms.ModelForm):
    """
    Formulario para que un administrador o dueño registre un nuevo comercio.
    """
    class Meta:
        model = Comercio
        fields = ('nombre', 'tipo', 'direccion', 'latitud', 'longitud', 'activo')
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'latitud': forms.TextInput(attrs={'placeholder': 'Latitud (ej: 40.7127)'}),
            'longitud': forms.TextInput(attrs={'placeholder': 'Longitud (ej: -74.0059)'}),
        }

class ProductoForm(forms.ModelForm):
    """
    Formulario para crear o editar un producto dentro de un comercio.
    """
    class Meta:
        model = Producto
        fields = ('nombre', 'descripcion', 'precio', 'disponible')
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
        }

# ----------------------------------------------------------------------
# 2. Formularios de Clientes (Realizar Pedidos)
# ----------------------------------------------------------------------

class PedidoDireccionForm(forms.ModelForm):
    """
    Formulario utilizado por el cliente para confirmar la dirección de entrega
    antes de finalizar el pedido.
    """
    class Meta:
        model = Pedido
        # Solo se piden los campos de dirección
        fields = ('direccion_entrega', 'lat_entrega', 'lon_entrega')
        widgets = {
            'direccion_entrega': forms.TextInput(attrs={'placeholder': 'Dirección exacta de entrega'}),
            'lat_entrega': forms.TextInput(attrs={'placeholder': 'Latitud de entrega'}),
            'lon_entrega': forms.TextInput(attrs={'placeholder': 'Longitud de entrega'}),
        }

class ItemPedidoForm(forms.Form):
    """
    Formulario simple utilizado para añadir un producto al carrito de compras.
    """
    cantidad = forms.IntegerField(
        min_value=1, 
        initial=1, 
        widget=forms.NumberInput(attrs={'class': 'input-cantidad', 'min': 1})
    )
    # Campo oculto para saber qué producto se está añadiendo
    producto_id = forms.IntegerField(widget=forms.HiddenInput())


# ----------------------------------------------------------------------
# 3. Formulario de Asignación de Servicios (Repartidores/Administradores)
# ----------------------------------------------------------------------

class DomicilioForm(forms.ModelForm):
    """
    Formulario utilizado por Repartidores o Administradores para asignar
    un vehículo, un repartidor y otros detalles del Pedido (Domicilio).
    """
    class Meta:
        model = Pedido
        # CRÍTICO: Incluir 'vehiculo_usado' y 'repartidor'
        fields = ('repartidor', 'vehiculo_usado', 'estado') 

    def __init__(self, *args, conductor_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 🔑 Lógica de Filtrado de Queryset para 'vehiculo_usado'
        if 'vehiculo_usado' in self.fields and conductor_user:
            
            # Filtra para mostrar SOLO los vehículos del usuario actual que estén APROBADOS
            if conductor_user.rol in ['conductor', 'repartidor_domicilios']:
                qs = Vehiculo.objects.filter(
                    conductor=conductor_user,
                    aprobado=True 
                ).order_by('placa')
                
                self.fields['vehiculo_usado'].queryset = qs
                
                # Muestra un mensaje si no hay vehículos disponibles
                if not qs.exists():
                    self.fields['vehiculo_usado'].empty_label = "No hay vehículos aprobados disponibles."
            else:
                # Si el usuario no es conductor/repartidor (ej. Admin), puede que no filtre
                # O puedes optar por ocultar el campo. Aquí lo dejamos vacío por defecto.
                self.fields['vehiculo_usado'].queryset = Vehiculo.objects.none()
        
        # Opcional: Filtra la lista de repartidores si es necesario (ej. solo mostrar repartidores activos)
        if 'repartidor' in self.fields:
             # Este es solo un ejemplo; ajusta el filtro según tus necesidades de UX.
             self.fields['repartidor'].queryset = UsuarioPersonalizado.objects.filter(rol='repartidor_domicilios', is_active=True)




# domicilios/forms.py (Añadir este bloque)
# Asegúrate de que Mensaje y UsuarioPersonalizado estén importados
from .models import Mensaje 

class MensajeForm(forms.ModelForm):
    """
    Formulario para enviar un mensaje dentro de un Pedido.
    """
    class Meta:
        model = Mensaje
        # Solo necesitamos que el usuario escriba el contenido.
        # 'pedido' y 'emisor' se asignarán en la vista.
        fields = ('contenido',) 
        widgets = {
            'contenido': forms.Textarea(attrs={
                'rows': 2, 
                'placeholder': 'Escribe tu mensaje aquí...',
                'class': 'form-control'
            }),
        }