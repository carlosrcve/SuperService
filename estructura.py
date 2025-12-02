SuperService/
├── SuperService/ 
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── **templates/** # Directorio principal para templates a nivel de proyecto
│   └── **base.html** # Template base general (útil para la estructura principal)
├── usuarios/
│   ├── migrations/
│   ├── **templates/**
│   │   └── **usuarios/** # Carpeta específica para templates de la app 'usuarios'
│   │       └── (archivo.html)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── transporte/
│   ├── migrations/
│   ├── **templates/**
│   │   └── **transporte/** # Carpeta específica para templates de la app 'transporte'
│   │       └── (archivo.html)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── domicilios/
│   ├── migrations/
│   ├── **templates/**
│   │   └── **domicilios/** # Carpeta específica para templates de la app 'domicilios'
│   │       └── (archivo.html)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── **static/** # Directorio principal para archivos estáticos
│   └── **core/** # Estáticos genéricos/compartidos por todo el proyecto
│       ├── **img/** # Imágenes y otros recursos visuales
│       ├── **js/** # Archivos JavaScript
│       ├── **scss/** # Archivos SCSS/Sass (para compilar a CSS)
│       └── **vendor/** # Librerías o frameworks de terceros (ej. Bootstrap)
└── manage.py