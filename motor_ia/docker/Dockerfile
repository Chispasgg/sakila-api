# Dockerfile para Motor de IA - Perkss API
FROM python:3.10-slim

LABEL maintainer "Patxi GG"

# Establecer el directorio de trabajo
WORKDIR /app

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Instalar dependencias del sistema necesarias para psycopg2
RUN apt-get update && 
RUN apt-get install -y gcc postgresql-client libpq-dev 
RUN rm -rf /var/lib/apt/lists/*

# Copiar archivo de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/ ./src/
COPY pytest.ini .

# Crear un usuario no root para ejecutar la aplicación
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exponer el puerto 2207 (puerto por defecto de la API)
EXPOSE 2207

# Comando por defecto para ejecutar la aplicación
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "2207"]
