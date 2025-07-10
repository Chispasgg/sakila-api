#!/bin/bash

echo "🎯 Preparando proyecto para pruebas..."
echo "======================================="

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


rm -r node_modules 
rm -r dist 
rm package-lock.json 

npm install 
npm run start:dev
