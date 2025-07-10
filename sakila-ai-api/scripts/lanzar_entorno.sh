#!/usr/bin/zsh

echo "🎯 Preparando entorno para pruebas..."
echo "======================================="

cd docker || { echo "Error: No se pudo cambiar al directorio docker."; exit 1; }

docker-compose up -d db redis
if [ $? -ne 0 ]; then
    echo "Error: No se pudo iniciar los contenedores de Docker."
    exit 1
fi

#cargamos la base de datos de sakila
cd ../sql_files || { echo "Error: No se pudo cambiar al directorio sql_files."; exit 1; }

#instalando dependencias
pip3 install -r requirements.txt

# volcando la base de datos
python3 generar_sakila_db.py
if [ $? -ne 0 ]; then
    echo "Error: No se pudo generar la base de datos Sakila."
    exit 1
fi

# Volvemos al directorio raíz del proyecto para ejecutar comandos de Prisma
cd .. || { echo "Error: No se pudo volver al directorio raíz."; exit 1; }

echo "🔄 Sincronizando esquema de Prisma con la base de datos..."
echo "========================================================="
# Cargar nvm si está instalado
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    echo "Cargando nvm..."
    source "$HOME/.nvm/nvm.sh"
elif [ -s "/usr/local/opt/nvm/nvm.sh" ]; then
    echo "Cargando nvm desde Homebrew..."
    source "/usr/local/opt/nvm/nvm.sh"
else
    echo "Error: nvm no está instalado."
    echo "Por favor instala nvm primero: https://github.com/nvm-sh/nvm"
    exit 1
fi

nvm use --lts || { echo "Error: No se pudo usar la versión LTS de Node.js."; exit 1; }
# Limpiar módulos y dependencias previas
rm -rf node_modules
rm -rf dist
rm package-lock.json

npm install

# Sincronizar esquema de Prisma con la base de datos (incluyendo tabla Feedback)
npx prisma db pull --force
if [ $? -ne 0 ]; then
    echo "Error: No se pudo sincronizar el esquema de Prisma."
    exit 1
fi

# Generar cliente TypeScript de Prisma
npx prisma generate
if [ $? -ne 0 ]; then
    echo "Error: No se pudo generar el cliente de Prisma."
    exit 1
fi

echo "✅ Entorno preparado correctamente!"
echo "📊 Base de datos Sakila cargada con tabla Feedback"
echo "🔧 Cliente Prisma generado y sincronizado"
echo "🐳 Contenedores Docker (db, redis) ejecutándose"