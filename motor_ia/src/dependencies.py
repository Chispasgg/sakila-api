"""
Gestión de dependencias para la API de recomendaciones.

Este módulo maneja la inyección de dependencias para FastAPI,
específicamente el servicio de base de datos utilizado por todos los endpoints.
"""

import os
from typing import Generator
from src.database.db_service import DatabaseService

# Configuración de base de datos desde variables de entorno con fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/sakila"
)

def get_db_service() -> Generator[DatabaseService, None, None]:
    """
    Dependency provider para el servicio de base de datos.
    
    Crea y proporciona una instancia de DatabaseService para inyección
    de dependencias en los endpoints de FastAPI.
    
    Yields:
        DatabaseService: Instancia del servicio de base de datos
        
    Note:
        Utiliza el patrón dependency injection de FastAPI.
        Las conexiones a BD se manejan dentro de DatabaseService.
    """
    db_service = DatabaseService(DATABASE_URL)
    try:
        yield db_service
    finally:
        # Cleanup si fuera necesario en el futuro
        # Por ahora DatabaseService maneja sus propias conexiones
        pass
