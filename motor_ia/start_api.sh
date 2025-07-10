#!/bin/bash

# Nombre del entorno virtual
VENV_NAME="venv"

# Puerto para Uvicorn
PORT=2207

echo "Iniciando la configuración y lanzamiento de la API..."

# 1. Crear el entorno virtual si no existe
if [ ! -d "$VENV_NAME" ]; then
    echo "Creando entorno virtual '$VENV_NAME'..."
    python3 -m venv "$VENV_NAME"
    if [ $? -ne 0 ]; then
        echo "Error: No se pudo crear el entorno virtual. Asegúrate de tener Python 3 instalado."
        exit 1
    fi
else
    echo "Entorno virtual '$VENV_NAME' ya existe."
fi

# 2. Activar el entorno virtual
echo "Activando entorno virtual..."
source "$VENV_NAME"/bin/activate

# 3. Instalar dependencias
if [ -f "requirements.txt" ]; then
    echo "Instalando dependencias desde requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: No se pudieron instalar las dependencias."
        exit 1
    fi
else
    echo "Advertencia: requirements.txt no encontrado. Saltando la instalación de dependencias."
fi

# 4. Lanzar la aplicación con Uvicorn
echo "Lanzando la API con Uvicorn en el puerto $PORT..."
# --host 0.0.0.0 permite que la API sea accesible desde otras máquinas en la red
uvicorn src.main:app --host 0.0.0.0 --port "$PORT" --reload --timeout-keep-alive 3600
# uvicorn src.main:app --workers 2 --host 0.0.0.0 --port "$PORT" --timeout-keep-alive 3600

# Desactivar el entorno virtual al salir (esto no se ejecutará si uvicorn se mantiene activo)
# deactivate
