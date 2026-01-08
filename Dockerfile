# ====================================================================
# ETAPA 1: BUILDER (Compilación y Resolución de Dependencias)
# ====================================================================
FROM python:3.12-slim-bullseye AS builder

# 1. Instalación atómica de dependencias del sistema operativo (Librerías de desarrollo)
# CRÍTICO: Se cambian los hosts a ftp.debian.org y security.debian.org para evitar el bloqueo de IP.
RUN echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'deb http://ftp.debian.org/debian bullseye main contrib non-free' > /etc/apt/sources.list && \
    echo 'deb http://ftp.debian.org/debian bullseye-updates main contrib non-free' >> /etc/apt/sources.list && \
    echo 'deb http://security.debian.org/debian-security bullseye-security/updates main contrib non-free' >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-transport-https ca-certificates build-essential git pkg-config libpq-dev default-libmysqlclient-dev libxml2-dev libxslt-dev zlib1g-dev \
    libjpeg-dev libpng-dev libssl-dev libffi-dev libmaxminddb-dev libpango1.0-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Configurar el directorio de trabajo y copiar archivos
WORKDIR /app
COPY requirements.in /app/

# 3. GESTIÓN DE DEPENDENCIAS ESTABLES (Comandos RUN separados y timeout extendido)
# Usamos un timeout largo (900s = 15min) y un mirror de PyPI alternativo y confiable.
# 3a. Instalar pip-tools
RUN pip install --default-timeout=900 pip-tools

# 3b. Compilar el requirements.in
RUN pip-compile requirements.in

# 3c. Instalar las dependencias (Django y Gunicorn) desde el mirror de PyPI
RUN pip install --default-timeout=900 --no-cache-dir -r requirements.txt --index-url https://pypi.python.org/simple

# 3d. SOLUCIÓN SPACY: Instalar la librería base de Spacy y el modelo grande (whl)
RUN pip install --default-timeout=900 --no-cache-dir spacy && \
    pip install --default-timeout=900 --no-cache-dir \
    https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl


# ====================================================================
# ETAPA 2: PRODUCTION (Contenedor Final Ligero)
# ====================================================================
FROM python:3.12-slim-bullseye AS production

# 1. Instalación atómica de dependencias de sistema necesarias para el RUNTIME
RUN echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'deb http://ftp.debian.org/debian bullseye main contrib non-free' > /etc/apt/sources.list && \
    echo 'deb http://ftp.debian.org/debian bullseye-updates main contrib non-free' >> /etc/apt/sources.list && \
    echo 'deb http://security.debian.org/debian-security bullseye-security/updates main contrib non-free' >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-transport-https ca-certificates libpq5 libmariadb3 openssl libffi7 libjpeg62-turbo libpng16-16 libxml2 libxslt1.1 \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libcairo2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Configuración de la aplicación
WORKDIR /app

# 3. Copiar los artefactos
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /app/requirements.txt /app/

# 4. Copiar el código del proyecto
COPY . /app/

# Exponer el puerto de Django
EXPOSE 8000

# Comando de Producción (Ruta explícita de Gunicorn)
CMD ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0:8000", "SuperService.wsgi:application"]