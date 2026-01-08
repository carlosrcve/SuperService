# SuperService/settings.py
"""
Configuración para el proyecto SuperService.
"""

import os
from pathlib import Path
from decouple import config # 🔑 AÑADIDO: Importar para cargar variables de entorno

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------------
# SEGURIDAD Y CLAVE SECRETA (CARGADAS DESDE .env)
# ----------------------------------------------------------------------

# 🔑 CORRECCIÓN: Cargar SECRET_KEY y DEBUG desde el entorno (más seguro).
SECRET_KEY = config('SECRET_KEY')

# Si DEBUG no está definido en el entorno, por defecto es False en producción.
DEBUG = config('DEBUG', default=False, cast=bool) 

# Cuando DEBUG=False, esta lista DEBE contener el dominio de tu servidor.
#ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0', 'superservice-api.onrender.com'] # Reemplazar con la URL real
#ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'host.docker.internal']
#ALLOWED_HOSTS = ['192.168.1.10', 'host.docker.internal', 'localhost', '127.0.0.1', '*' ]
ALLOWED_HOSTS = ['norbe-final.loca.lt', 'localhost', '127.0.0.1', '.loca.lt']

ALLOWED_HOSTS = ['*']
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
    'django.contrib.humanize', # Ya estaba

    # Librerías de terceros y seguridad
    'corsheaders',              # 🔑 CORRECCIÓN: Colocado aquí para mejor organización
    'rest_framework',           # DRF
    'crispy_forms',             # Formulario
    'crispy_bootstrap5',        # Estilos para Crispy Forms
    'mathfilters',
    
    # Aplicación de Channels
    'channels',

    # Aplicaciones del Proyecto SuperService
    'usuarios',
    'transporte',
    'domicilios',
]

# ----------------------------------------------------------------------
# MIDDLEWARE (ORDEN CRÍTICO PARA WHITENOISE Y CORS)
# ----------------------------------------------------------------------

MIDDLEWARE = [
    # 1. Seguridad (Debe ir primero)
    'django.middleware.security.SecurityMiddleware',
    # 2. WhiteNoise (Debe ir justo después de SecurityMiddleware para estáticos)
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'csp.middleware.CSPMiddleware', # CSP

    # 3. CORS (Debe ir antes de Common y CSRF)
    'corsheaders.middleware.CorsMiddleware',

    # 4. Django Default
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SuperService.urls'

# ----------------------------------------------------------------------
# TEMPLATES (Rutas de Plantillas)
# ----------------------------------------------------------------------
# ... (Tu configuración de TEMPLATES no ha cambiado) ...

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
# CONFIGURACIÓN DE CHANNELS/ASGI (CORRECTA)
# ----------------------------------------------------------------------

ASGI_APPLICATION = 'SuperService.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        # Usar la capa en memoria en desarrollo, o en caso de que Redis no esté configurado.
        'BACKEND': config('CHANNEL_LAYER_BACKEND', default='channels.layers.InMemoryChannelLayer'),
    },
}

# ----------------------------------------------------------------------
# CONFIGURACIÓN TRADICIONAL DE WSGI Y BASE DE DATOS
# ----------------------------------------------------------------------

WSGI_APPLICATION = 'SuperService.wsgi.application'

# 🔑 CORRECCIÓN CRÍTICA: Base de datos que se adapta a DEBUG
if DEBUG:
    # Usar SQLite en desarrollo local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Usar PostgreSQL o MySQL en producción, cargando credenciales de las variables de entorno
    DATABASES = {
        'default': {
            # Siempre debe buscar la clave 'DB_ENGINE'
            'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'), 
            
            # 🔑 CORRECTO: Busca la clave 'DB_NAME'
            'NAME': config('DB_NAME'), 
            
            # 🔑 CORRECTO: Busca la clave 'DB_USER'
            'USER': config('DB_USER'), 
            
            # Correcto: Busca la clave 'DB_PASSWORD'
            'PASSWORD': config('DB_PASSWORD'), 
            
            # 🔑 CORRECTO: Busca la clave 'DB_HOST'
            'HOST': config('DB_HOST'),
            
            # Correcto: Busca la clave 'DB_PORT'
            'PORT': config('DB_PORT', default='5432'), 
        }
    }


# ----------------------------------------------------------------------
# AUTENTICACIÓN Y ROLES
# ----------------------------------------------------------------------

AUTH_USER_MODEL = 'usuarios.UsuarioPersonalizado'
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# ... (VALIDACIÓN DE CONTRASEÑAS, IDIOMA Y ZONA HORARIA sin cambios) ...

# ----------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS Y MEDIA (WHITENOISE)
# ----------------------------------------------------------------------

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), 
]

# 🔑 NECESARIO PARA WHITENOISE: Define la carpeta donde se copiarán los estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 🔑 Configuración de WhiteNoise para servir los archivos estáticos en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# 🔑 AÑADIDO: Configuración de archivos de Media (para imágenes de usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ----------------------------------------------------------------------
# SEGURIDAD Y CORS (ADAPTACIÓN A PRODUCCIÓN)
# ----------------------------------------------------------------------

# 🔑 CORRECCIÓN: Estos deben ser True en producción (DEBUG=False)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)


# 🔑 CORRECCIÓN: Lógica para CORS que se ajusta a DEBUG
if DEBUG:
    # Permitir todo en desarrollo
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # En producción, restringir solo a la URL de la aplicación móvil (React Native)
    CORS_ALLOWED_ORIGINS = [
        "https://tu-dominio-react-native.com", # Dominio de la app web/móvil si existe
        # Ejemplo para pruebas en emulador/Expo:
        # "http://localhost:8081",
        # "exp://192.168.1.100:8081",
    ]


# ----------------------------------------------------------------------
# CSP Y OTROS (Se mantienen tus valores)
# ----------------------------------------------------------------------
# ...


# Añade esto al final de tu settings.py
CSRF_TRUSTED_ORIGINS = [
    'https://norbe-final.loca.lt',
    'http://192.168.1.10:8080',  # <--- Agrega esto para que el celular pueda enviar datos
    'http://127.0.0.1:8080'
]

# 3. Verifica que el CORS esté abierto en modo DEBUG (esto también lo tienes bien)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

