# SuperService/settings.py
"""
Configuración para el proyecto SuperService.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------------
# SEGURIDAD Y CLAVE SECRETA
# ----------------------------------------------------------------------

# WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tu-super-secreta-clave-aqui-usa-variables-de-entorno-en-produccion'

# WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# ----------------------------------------------------------------------
# APLICACIONES (APPS)
# ----------------------------------------------------------------------

INSTALLED_APPS = [
    # Aplicaciones por defecto de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'crispy_forms',  # Formulario
    'crispy_bootstrap5',  # Estilos para Crispy Forms
    
    # Librerías de terceros 
    'mathfilters',
    
    # Aplicación de Channels (¡CRÍTICA PARA EL CHAT!)
    'channels',

    # 🛑 Añade esta línea
    'django.contrib.humanize',

    # Aplicaciones del Proyecto SuperService
    'usuarios',    # Manejo de usuarios personalizados y roles
    'transporte',
    'domicilios',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # 👈 ¡Añadir aquí!
   
]

ROOT_URLCONF = 'SuperService.urls'

# ----------------------------------------------------------------------
# TEMPLATES (Rutas de Plantillas)
# ----------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ----------------------------------------------------------------------
# CONFIGURACIÓN DE CHANNELS/ASGI (¡CORRECCIÓN CLAVE!)
# ----------------------------------------------------------------------

# 1. Define la aplicación principal ASGI.
# ESTA LÍNEA FUE CORREGIDA DE 'myproject' A 'SuperService'.
ASGI_APPLICATION = 'SuperService.asgi.application' # ✅ Debe ser ASGI_APPLICATION

# 2. Configura la capa de canales (CRÍTICO para el broadcast):
CHANNEL_LAYERS = {
    'default': {
        # Esta es la configuración MÍNIMA para desarrollo. 
        # Si no tienes Redis, usa esta capa en memoria:
        'BACKEND': 'channels.layers.InMemoryChannelLayer', 
    },
    # Opcional (si usas Redis):
    # 'default': {
    #     'BACKEND': 'channels_redis.pubsub.RedisChannelLayer',
    #     'CONFIG': {
    #         "hosts": [('127.0.0.1', 6379)],
    #     },
    # },
}

# ----------------------------------------------------------------------
# CONFIGURACIÓN TRADICIONAL DE WSGI Y BASE DE DATOS
# ----------------------------------------------------------------------

WSGI_APPLICATION = 'SuperService.wsgi.application'

'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 👈 CAMBIAR AQUÍ
        'NAME': 'nombre_bd',
        'USER': 'usuario_bd',
        'PASSWORD': 'password_bd',
        'HOST': 'host_bd',
        'PORT': '3306', # Puerto por defecto de MySQL
    }
}


# ----------------------------------------------------------------------
# AUTENTICACIÓN Y ROLES
# ----------------------------------------------------------------------

AUTH_USER_MODEL = 'usuarios.UsuarioPersonalizado'
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'


# ----------------------------------------------------------------------
# VALIDACIÓN DE CONTRASEÑAS
# ----------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ----------------------------------------------------------------------
# IDIOMA Y ZONA HORARIA
# ----------------------------------------------------------------------

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True


# ARCHIVOS ESTÁTICOS Y CRISPY FORMS
# ----------------------------------------------------------------------

# 1. La URL que se usa en las plantillas (siempre debe ser la única)
STATIC_URL = '/static/' 

# 2. Directorios adicionales donde Django debe buscar archivos estáticos.
# Esta línea le dice a Django: "Busca la carpeta 'static' dentro de la ruta BASE_DIR"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), 
]

# Configuración de Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5" 
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Origen por defecto: solo recursos propios
CSP_DEFAULT_SRC = ("'self'",)

# Permite imágenes (mosaicos de mapa e iconos de marcador)
CSP_IMG_SRC = (
    "'self'",
    "data:",                       # Imágenes incrustadas (base64)
    "*.tile.openstreetmap.org",    # Mosaicos de OpenStreetMap
    "raw.githubusercontent.com",   # Iconos de marcador de colores (leaflet-color-markers)
    "https://cdnjs.cloudflare.com" # Recursos de imagen o datos cargados desde cdnjs/Cloudflare
)

# Permite hojas de estilo
CSP_STYLE_SRC = (
    "'self'", 
    "https://unpkg.com", 
    "https://cdnjs.cloudflare.com", 
    "'unsafe-inline'"             # Necesario para que Leaflet inyecte estilos dinámicos
)

# Permite scripts de JavaScript
CSP_SCRIPT_SRC = (
    "'self'", 
    "https://unpkg.com", 
    "https://cdnjs.cloudflare.com"
)


# Si estás ejecutando en HTTP (local), debe ser False
CSRF_COOKIE_SECURE = False 

# Si estás ejecutando en HTTP (local), debe ser False
SESSION_COOKIE_SECURE = False


# Permite a cualquier frontend conectarse temporalmente (solo en desarrollo inicial)
CORS_ALLOW_ALL_ORIGINS = True

# O la opción más segura (reemplaza esto después de desplegar):
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:8081", # Para pruebas en emulador React Native
# ]


# Configuración de WhiteNoise para comprimir y servir archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Directorio donde Django recolectará los archivos estáticos para WhiteNoise
STATIC_ROOT = BASE_DIR / 'staticfiles'