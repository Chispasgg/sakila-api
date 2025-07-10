#!/bin/bash

cd docker || { echo "❌ Error: No se pudo cambiar al directorio docker."; exit 1; }
docker-compose down
echo "✅ Docker generales detenidos"
echo ""
cd ../sakila-ai-api/docker
docker-compose down
echo "✅ Docker temporales detenidos"
echo ""
cd ../scripts
./lanzar_run.sh
