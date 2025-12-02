# transporte/forms.py
from django import forms
from .models import Viaje, Vehiculo, SolicitudAsistencia,MensajeViaje


# ----------------------------------------------------------------------
# 1. Formularios para Clientes (Solicitar Servicios)
# ----------------------------------------------------------------------
'''
class ViajeSolicitudForm(forms.ModelForm):
    """
    Formulario que usa el cliente para solicitar un viaje. 
    Solo requiere las coordenadas de origen y destino.
    """
    
    # Campos adicionales para mejor experiencia del usuario (no en el modelo)
    nombre_origen = forms.CharField(max_length=255, required=False, help_text="Ej: Mi casa o Calle Falsa 123")
    nombre_destino = forms.CharField(max_length=255, required=False, help_text="Ej: Oficina o Centro Comercial")
    
    class Meta:
        model = Viaje
        # Incluye solo los campos de ubicación, el cliente y el estado se asignan en la vista
        fields = (
            'origen_lat', 'origen_lon', 
            'destino_lat', 'destino_lon'
        )
        widgets = {
            'origen_lat': forms.TextInput(attrs={'placeholder': 'Latitud de Origen', 'required': 'required'}),
            'origen_lon': forms.TextInput(attrs={'placeholder': 'Longitud de Origen', 'required': 'required'}),
            'destino_lat': forms.TextInput(attrs={'placeholder': 'Latitud de Destino', 'required': 'required'}),
            'destino_lon': forms.TextInput(attrs={'placeholder': 'Longitud de Destino', 'required': 'required'}),
        }
'''
class ViajeSolicitudForm(forms.ModelForm):
    """
    Formulario que usa el cliente para solicitar un viaje.
    Maneja solo los detalles del servicio y los campos de texto auxiliares.
    """
    
    # 🟢 CAMPOS AUXILIARES (NO GESTIONADOS POR META.FIELDS):
    # Estos campos se usan para enviar el nombre de la dirección desde el frontend
    # y deben ser guardados manualmente en la vista (viaje.nombre_origen = ...).
    nombre_origen = forms.CharField(
        max_length=255, 
        required=False, 
        help_text="Ej: Mi casa o Calle Falsa 123",
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Punto de Partida (Texto Auxiliar)'})
    )
    
    nombre_destino = forms.CharField(
        max_length=255, 
        required=False, 
        help_text="Ej: Oficina o Centro Comercial",
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Destino Final (Texto Auxiliar)'})
    )
    
    # 🛑 NOTA: Los campos tipo_servicio y notas_conductor NO se definen aquí 
    # explícitamente porque ModelForm los toma automáticamente de la clase Meta.
    
    class Meta:
        model = Viaje
        # CRÍTICO: Incluir solo los campos del modelo que el usuario debe llenar
        fields = ['tipo_servicio', 'notas_conductor']
        
        # 💡 Los widgets y labels anulan los valores por defecto del ModelForm
        widgets = {
            'tipo_servicio': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'tipoServicio', 'required': 'required'}),
            'notas_conductor': forms.Textarea(attrs={'class': 'form-control', 'id': 'notas', 'rows': 2, 'placeholder': 'Ej: Estoy en la esquina del banco.'}),
        }
        
        labels = {
            'tipo_servicio': 'Tipo de Vehículo',
            'notas_conductor': 'Notas para el Conductor (Opcional)',
        }
        
class AsistenciaSolicitudForm(forms.ModelForm):
    """
    Formulario que usa el cliente para solicitar asistencia vial.
    """
    class Meta:
        model = SolicitudAsistencia
        # Incluye el tipo de asistencia y la ubicación
        fields = (
            'tipo_asistencia', 
            'ubicacion_lat', 'ubicacion_lon', 
            'descripcion'
        )
        widgets = {
            'tipo_asistencia': forms.Select(attrs={'required': 'required'}),
            'ubicacion_lat': forms.TextInput(attrs={'placeholder': 'Latitud del Incidente', 'required': 'required'}),
            'ubicacion_lon': forms.TextInput(attrs={'placeholder': 'Longitud del Incidente', 'required': 'required'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Detalla qué pasó (Ej: Se me estalló una llanta)'}),
        }

# ----------------------------------------------------------------------
# 2. Formularios para Conductores (Gestión de Vehículos)
# ----------------------------------------------------------------------

class VehiculoRegistroForm(forms.ModelForm):
    """
    Formulario para que un conductor/repartidor registre un vehículo.
    El campo 'conductor' se asignará automáticamente en la vista.
    """
    class Meta:
        model = Vehiculo
        # Excluir 'conductor' y 'aprobado' que se manejan en la vista y por el administrador
        fields = (
            'tipo', 
            'modelo', 
            'placa', 
            'color'
        )
        widgets = {
            'placa': forms.TextInput(attrs={'placeholder': 'Ej: XYZ-123'}),
        }


# transporte/forms.py (Definiciones de Clases)

# ... (otras clases de formulario) ...

class MensajeViajeForm(forms.ModelForm):
    """Formulario para enviar mensajes en un Viaje."""
    class Meta:
        model = MensajeViaje
        fields = ['contenido']
        widgets = {
            'contenido': forms.TextInput(attrs={
                'placeholder': 'Escribe un mensaje aquí...',
                'class': 'form-control'
            }),
        }