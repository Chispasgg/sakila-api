#!/bin/bash

# Script de utilidades para Docker - Motor de IA Perkss
# Uso: ./docker-utils.sh [comando]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado. Por favor instala Docker primero."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
        exit 1
    fi
}

# Configurar archivo .env si no existe
setup_env() {
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        print_warning "Archivo .env no encontrado. Creando desde .env.example..."
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        print_warning "Por favor edita el archivo .env con tus configuraciones antes de continuar."
        exit 1
    fi
}

# Construir y ejecutar servicios
start_dev() {
    print_status "Iniciando servicios en modo desarrollo..."
    cd "$SCRIPT_DIR"
    docker-compose up --build -d
    print_success "Servicios iniciados. API disponible en http://localhost:2207"
}

# Ejecutar en modo producción
start_prod() {
    print_status "Iniciando servicios en modo producción..."
    cd "$SCRIPT_DIR"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
    print_success "Servicios iniciados en modo producción."
}

# Detener servicios
stop() {
    print_status "Deteniendo servicios..."
    cd "$SCRIPT_DIR"
    docker-compose down
    print_success "Servicios detenidos."
}

# Ver logs
logs() {
    local service=${1:-motor_ia_api}
    print_status "Mostrando logs de $service..."
    cd "$SCRIPT_DIR"
    docker-compose logs -f "$service"
}

# Backup de base de datos
backup_db() {
    local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    print_status "Creando backup de la base de datos..."
    cd "$SCRIPT_DIR"
    docker-compose exec postgres pg_dump -U postgres sakila > "$backup_file"
    print_success "Backup creado: $backup_file"
}

# Restaurar base de datos
restore_db() {
    local backup_file=$1
    if [ -z "$backup_file" ]; then
        print_error "Uso: $0 restore <archivo_backup>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Archivo de backup no encontrado: $backup_file"
        exit 1
    fi
    
    print_status "Restaurando base de datos desde $backup_file..."
    cd "$SCRIPT_DIR"
    docker-compose exec -T postgres psql -U postgres sakila < "$backup_file"
    print_success "Base de datos restaurada."
}

# Limpiar todo (¡CUIDADO!)
clean() {
    print_warning "¡ATENCIÓN! Esto eliminará todos los contenedores, volúmenes e imágenes."
    read -p "¿Estás seguro? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$SCRIPT_DIR"
        docker-compose down -v --rmi all
        print_success "Limpieza completada."
    else
        print_status "Operación cancelada."
    fi
}

# Mostrar estado de servicios
status() {
    print_status "Estado de los servicios:"
    cd "$SCRIPT_DIR"
    docker-compose ps
}

# Mostrar ayuda
show_help() {
    echo "Motor de IA - Docker Utilities"
    echo
    echo "Uso: $0 [comando]"
    echo
    echo "Comandos disponibles:"
    echo "  start-dev    - Iniciar servicios en modo desarrollo"
    echo "  start-prod   - Iniciar servicios en modo producción"
    echo "  stop         - Detener todos los servicios"
    echo "  restart      - Reiniciar servicios"
    echo "  status       - Mostrar estado de servicios"
    echo "  logs [servicio] - Mostrar logs (por defecto: motor_ia_api)"
    echo "  backup       - Crear backup de la base de datos"
    echo "  restore <archivo> - Restaurar base de datos desde backup"
    echo "  clean        - Limpiar todos los contenedores y volúmenes"
    echo "  help         - Mostrar esta ayuda"
    echo
    echo "Ejemplos:"
    echo "  $0 start-dev"
    echo "  $0 logs postgres"
    echo "  $0 backup"
    echo "  $0 restore backup_20240101_120000.sql"
}

# Función principal
main() {
    check_docker
    
    case "${1:-help}" in
        "start-dev")
            setup_env
            start_dev
            ;;
        "start-prod")
            setup_env
            start_prod
            ;;
        "stop")
            stop
            ;;
        "restart")
            stop
            sleep 2
            start_dev
            ;;
        "status")
            status
            ;;
        "logs")
            logs "$2"
            ;;
        "backup")
            backup_db
            ;;
        "restore")
            restore_db "$2"
            ;;
        "clean")
            clean
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Ejecutar función principal con todos los argumentos
main "$@"
