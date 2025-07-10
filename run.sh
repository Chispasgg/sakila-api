#!/bin/bash

cd docker || { echo "❌ Error: No se pudo cambiar al directorio docker."; exit 1; }
docker-compose down
echo "✅ Docker detenidos"
echo ""
cd ../sakila-ai-api/scripts
./lanzar_run.sh
