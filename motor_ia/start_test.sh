#!/bin/bash

# Script para ejecutar tests del motor de IA
# Configuración simple y directa para testing

VENV_NAME="venv"

echo "🧪 Iniciando tests del Motor de IA..."

# 1. Crear entorno virtual si no existe
if [ ! -d "$VENV_NAME" ]; then
    echo "📦 Creando entorno virtual '$VENV_NAME'..."
    python3 -m venv "$VENV_NAME"
    if [ $? -ne 0 ]; then
        echo "❌ Error: No se pudo crear el entorno virtual."
        exit 1
    fi
fi

# 2. Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source "$VENV_NAME"/bin/activate

# 3. Instalar dependencias si es necesario
if [ -f "requirements.txt" ]; then
    echo "📥 Instalando/actualizando dependencias..."
    pip install -r requirements.txt --quiet
fi

# 4. Ejecutar tests
echo "🚀 Ejecutando tests con pytest..."
pytest

echo "✅ Tests completados."
