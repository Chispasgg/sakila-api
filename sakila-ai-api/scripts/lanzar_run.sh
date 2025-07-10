#!/bin/bash

echo "🔄 Iniciando Sakila AI Recommendation Engine API"
cd ..
# comentar esto si ya se tiene un .env configurado
# -------------------
cp .env.example .env
# -------------------
echo " Sakila AI Recommendation Engine API"
echo "======================================"
echo ""

# Función para cargar NVM
load_nvm() {
    echo "🔧 Configurando Node.js..."
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        echo "📦 Cargando nvm..."
        source "$HOME/.nvm/nvm.sh"
    elif [ -s "/usr/local/opt/nvm/nvm.sh" ]; then
        echo "📦 Cargando nvm desde Homebrew..."
        source "/usr/local/opt/nvm/nvm.sh"
    else
        echo "❌ Error: nvm no está instalado."
        echo "Por favor instala nvm primero: https://github.com/nvm-sh/nvm"
        exit 1
    fi

    nvm use --lts || { echo "❌ Error: No se pudo usar la versión LTS de Node.js."; exit 1; }
    echo "✅ Node.js $(node --version) configurado"
}

# Función para configuración inicial del entorno
setup_environment() {
    echo ""
    echo "🚀 CONFIGURACIÓN INICIAL DEL ENTORNO"
    echo "===================================="
    
    # 1. Levantar servicios Docker
    echo "🐳 Iniciando servicios Docker (PostgreSQL + Redis)..."
    cd docker || { echo "❌ Error: No se pudo cambiar al directorio docker."; exit 1; }
    
    docker-compose up -d db redis
    if [ $? -ne 0 ]; then
        echo "❌ Error: No se pudo iniciar los contenedores de Docker."
        exit 1
    fi
    echo "✅ Servicios Docker iniciados"
    
    sleep 10  # Esperar a que los servicios se levanten correctamente

    # 2. Configurar base de datos Sakila
    echo "📊 Configurando base de datos Sakila..."
    cd ../sql_files || { echo "❌ Error: No se pudo cambiar al directorio sql_files."; exit 1; }
    
    # Instalar dependencias Python
    echo "🐍 Instalando dependencias Python..."
    pip3 install -r requirements.txt
    
    # Generar base de datos
    echo "🗄️ Generando base de datos Sakila..."
    python3 generar_sakila_db.py
    if [ $? -ne 0 ]; then
        echo "❌ Error: No se pudo generar la base de datos Sakila."
        exit 1
    fi
    echo "✅ Base de datos Sakila creada"
    
    # 3. Volver al directorio raíz y configurar Node.js
    cd .. || { echo "❌ Error: No se pudo volver al directorio raíz."; exit 1; }
    
    load_nvm
    
    # 4. Limpiar e instalar dependencias
    echo "🧹 Limpiando instalación previa..."
    rm -rf node_modules dist package-lock.json 2>/dev/null
    
    echo "📦 Instalando dependencias npm..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error: No se pudo instalar las dependencias."
        exit 1
    fi
    
    # 5. Configurar Prisma
    echo "🔄 Sincronizando esquema de Prisma..."
    npx prisma db pull --force
    if [ $? -ne 0 ]; then
        echo "❌ Error: No se pudo sincronizar el esquema de Prisma."
        exit 1
    fi
    
    echo "⚙️ Generando cliente Prisma..."
    npx prisma generate
    if [ $? -ne 0 ]; then
        echo "❌ Error: No se pudo generar el cliente de Prisma."
        exit 1
    fi
    
    # 6. Parar los servicios Docker
    echo "🐳 Parando servicios Docker (PostgreSQL + Redis)..."
    cd docker || { echo "❌ Error: No se pudo cambiar al directorio docker."; exit 1; }
    
    docker-compose down db redis
    if [ $? -ne 0 ]; then
        echo "❌ Error: No se pudo iniciar los contenedores de Docker."
        exit 1
    fi
    echo "✅ Servicios Docker parados"
    
    sleep 10  # Esperar a que los servicios se levanten correctamente
    cd .. || { echo "❌ Error: No se pudo volver al directorio raíz."; exit 1; }
    echo ""
    echo "🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE"
    echo "========================================"
    echo "✅ Servicios Docker ejecutándose"
    echo "✅ Base de datos Sakila cargada"
    echo "✅ Tabla feedback creada"
    echo "✅ Cliente Prisma generado"
    echo "✅ Dependencias instaladas"
    echo "✅ Docker detenidos"
    echo ""
}


# FLUJO PRINCIPAL INTERACTIVO
echo "🎯 LANZADOR RUN"
echo "==============="

# Preguntar si quiere ejecutar configuración inicial
echo ""
echo "❓ ¿Desea ejecutar la configuración inicial del entorno?"
echo "   (Esto incluye: Docker, Base de datos, Prisma, dependencias)"
echo ""
echo "   s/S = Sí, ejecutar configuración completa"
echo "   n/N = No, saltar configuración"
echo ""
echo -n "👉 Respuesta [s/N]: "
read setup_choice

case "$setup_choice" in
    [sS]|[sS][iI])
        echo ""
        echo " Borramos la base de datos existente de sakila"
        echo "========================================="
        sudo rm -r ../datos_docker/postgres-data
        sudo rm -r ../datos_docker/redis
        echo "========================================="
        load_nvm
        setup_environment
        ;;
    [nN]|[nN][oO]|"")
        echo "⏭️ Saltando configuración inicial..."
        load_nvm
        ;;
    *)
        echo "❌ Respuesta no válida. Saltando configuración..."
        load_nvm
        ;;
esac

# Volvemos a la carpeta raiz
cd ..

# levantamos el docker general
echo ""
echo "🐳 LEVANTANDO SERVICIOS DOCKER CON TODO"
echo "====================================="
cd docker || { echo "❌ Error: No se pudo cambiar al directorio docker."; exit 1; }
docker-compose up -d

# Esperar a que todos los servicios estén healthy
echo "⏳ Esperando a que los contenedores estén healthy..."
docker-compose ps

while [ "$(docker-compose ps | grep -c '(healthy)')" -lt 3 ]; do
  sleep 2
  docker-compose ps
done

echo "Servicios OK y corriendo"
echo "========================="
echo "🚀 Sistema completo iniciado, a jugar"
echo "✨ EJECUCIÓN COMPLETADA"
echo "======================"
