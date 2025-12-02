# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import UsuarioPersonalizado, PerfilConductor

# ----------------------------------------------------------------------
# 1. Formulario de Inicio de Sesión
# ----------------------------------------------------------------------

class LoginForm(AuthenticationForm):
    """
    Formulario estándar de Django para iniciar sesión. 
    Hereda de AuthenticationForm y solo personalizamos el estilo si es necesario.
    """
    username = forms.CharField(
        label='Nombre de Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Ej: usuario123'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingresa tu contraseña'})
    )

# ----------------------------------------------------------------------
# 2. Formulario de Registro de Clientes
# ----------------------------------------------------------------------

class ClienteRegistroForm(UserCreationForm):
    """
    Formulario para registrar un cliente. Utiliza UserCreationForm de Django 
    para manejar la creación de la contraseña de forma segura.
    """
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellido', max_length=150)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UsuarioPersonalizado
        fields = ('username', 'first_name', 'last_name', 'email')
    
    def save(self, commit=True):
        # Aseguramos que el rol sea 'cliente' al guardar
        user = super().save(commit=False)
        user.rol = 'cliente'
        if commit:
            user.save()
        return user

# ----------------------------------------------------------------------
# 3. Formulario de Registro de Conductores/Repartidores
# ----------------------------------------------------------------------


# usuarios/forms.py (Solo la clase ConductorRegistroForm)

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

UsuarioPersonalizado = get_user_model() 
# ... (otras clases de formulario: LoginForm, ClienteRegistroForm)

# ----------------------------------------------------------------------
# 3. Formulario de Registro de Conductores/Repartidores (OPTIMIZADO)
# ----------------------------------------------------------------------

# usuarios/forms.py (Clase ConductorRegistroForm corregida)

class ConductorRegistroForm(UserCreationForm):
    """
    Formulario para registrar un proveedor de servicios (Conductor/Repartidor).
    """
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellido', max_length=150)
    email = forms.EmailField(required=True)
    
    ROL_CHOICES = [
        ('conductor', 'Conductor de Viajes / Asistencia Vial'),
        ('repartidor_domicilios', 'Repartidor de Domicilios'),
    ]
    rol = forms.ChoiceField(
        choices=ROL_CHOICES, 
        label="Quiero ser",
        widget=forms.RadioSelect
    )
    
    licencia = forms.CharField(
        max_length=50, 
        label="Número de Licencia de Conducir",
        help_text="Necesario para verificación y aprobación del administrador."
    )
    
    class Meta:
        model = UsuarioPersonalizado
        fields = ('username', 'first_name', 'last_name', 'email') 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ELIMINAR O COMENTAR las siguientes dos líneas.
        # Estas líneas son redundantes y causan el KeyError.
        # self.fields['password'].required = True
        # self.fields['password2'].required = True

    # --- Métodos de Limpieza y Validación ---
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # 1. Validación de Unicidad de Email
        if UsuarioPersonalizado.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado. Por favor, usa otro.")
        
        return email

    def clean_username(self):
        # 2. Validación de Unicidad de Username (ya UserCreationForm lo hace, pero la pasamos)
        username = self.cleaned_data['username']
        return username
    
    def clean(self):
        # 🔑 CORRECCIÓN APLICADA: Solo llamar a super().clean() una vez y devolver cleaned_data.
        cleaned_data = super().clean()
        return cleaned_data

    # --- Método de Guardado ---
    def save(self, commit=True):
        user = super().save(commit=False)
        
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")
        user.rol = self.cleaned_data.get("rol")

        if commit:
            user.save()
        
        return user