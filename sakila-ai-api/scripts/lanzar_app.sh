#!/bin/bash

cd ..
echo " Sakila AI Recommendation Engine API"
echo "======================================"
echo ""

# Función para mostrar ayuda
show_help() {
    echo "📖 Uso del script:"
    echo "  ./lanzar_app.sh [opción]"
    echo ""
    echo "Opciones:"
    echo "  --setup, -s     Solo ejecutar configuración inicial"
    echo "  --dev, -d       Lanzar en modo desarrollo"
    echo "  --test, -t      Lanzar pruebas E2E"
    echo "  --live          Lanzar pruebas live"
    echo "  --help, -h      Mostrar esta ayuda"
    echo ""
    echo "Sin opciones: Pregunta por configuración inicial y luego ejecuta modo test"
}

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
    
    echo ""
    echo "🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE"
    echo "========================================"
    echo "✅ Servicios Docker ejecutándose"
    echo "✅ Base de datos Sakila cargada"
    echo "✅ Tabla feedback creada"
    echo "✅ Cliente Prisma generado"
    echo "✅ Dependencias instaladas"
    echo ""
}

# Función para ejecutar en modo desarrollo
run_dev_mode() {
    echo "🔨 MODO DESARROLLO"
    echo "=================="
    load_nvm
    echo "🚀 Iniciando aplicación en modo desarrollo..."
    npm run start:dev
}

# Función para ejecutar pruebas E2E
run_test_e2e() {
    echo "🧪 PRUEBAS E2E (En Memoria)"
    echo "=========================="
    load_nvm
    echo "🧪 Ejecutando pruebas End-to-End..."
    npx jest --config ./test/jest-e2e.json
}

# Función para ejecutar pruebas live
run_test_live() {
    echo "🌐 PRUEBAS LIVE (Servidor Real)"
    echo "=============================="
    load_nvm
    echo "🌐 Ejecutando pruebas contra servidor en vivo..."
    npx jest --config ./jest-live.json
}

# Procesar argumentos de línea de comandos
case "$1" in
    --setup|-s)
        setup_environment
        exit 0
        ;;
    --dev|-d)
        load_nvm
        run_dev_mode
        exit 0
        ;;
    --test|-t)
        load_nvm
        run_test_e2e
        exit 0
        ;;
    --live)
        load_nvm
        run_test_live
        exit 0
        ;;
    --help|-h)
        show_help
        exit 0
        ;;
    "")
        # Sin argumentos: flujo interactivo
        ;;
    *)
        echo "❌ Opción desconocida: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

# FLUJO PRINCIPAL INTERACTIVO
echo "🎯 LANZADOR PRINCIPAL"
echo "===================="

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

# Asegurar que NVM esté cargado antes de ejecutar pruebas
if [ -z "$setup_choice" ] || [ "$setup_choice" != "s" ] && [ "$setup_choice" != "S" ] && [ "$setup_choice" != "si" ] && [ "$setup_choice" != "SI" ]; then
    load_nvm
fi

# Ejecutar pruebas E2E por defecto
echo ""
echo "🧪 EJECUTANDO PRUEBAS E2E"
echo "========================="
echo "🚀 Iniciando pruebas End-to-End en memoria..."
echo ""

run_test_e2e

echo ""
echo "✨ EJECUCIÓN COMPLETADA"
echo "======================"
echo "📊 Revisa los resultados de las pruebas arriba"
echo "🌐 Para modo desarrollo: ./lanzar_app.sh --dev"
echo "🧪 Para pruebas live: ./lanzar_app.sh --live"
echo "📖 Para ayuda: ./lanzar_app.sh --help"
