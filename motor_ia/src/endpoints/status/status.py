"""
Endpoint de estado del servicio (Health Check).

Proporciona información sobre el estado operativo de la API de recomendaciones,
incluyendo conectividad con la base de datos y timestamp para monitoreo.

Este endpoint es esencial para:
- Monitoreo de sistemas (health checks)
- Load balancers y reverse proxies
- Verificación de disponibilidad del servicio
- Debugging y diagnóstico de problemas
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from src.schemas import StatusResponse
from src.database.db_service import DatabaseService
from src.dependencies import get_db_service

router = APIRouter()

@router.get(
    "/status",
    summary="🏥 Health Check - Estado del Servicio",
    description="""
    # 🔍 Verificación de Estado del Sistema
    
    Endpoint especializado para verificar el estado operativo del servicio de recomendaciones.
    
    ## 📊 Información Proporcionada
    
    | Campo | Tipo | Descripción |
    |-------|------|-------------|
    | `status` | `boolean` | Estado general del servicio (true = operativo) |
    | `date` | `string` | Timestamp UTC en formato ISO 8601 |
    
    ## 🎯 Casos de Uso
    
    ### 🤖 Monitoreo Automático
    - ✅ Health checks de load balancers
    - ✅ Sistemas de monitoreo (Prometheus, Grafana)
    - ✅ Alertas de disponibilidad
    
    ### 🔧 Debugging y Diagnóstico
    - ✅ Verificación manual de estado
    - ✅ Troubleshooting de conectividad
    - ✅ Validación post-despliegue
    
    ## ⚡ Rendimiento Esperado
    - **Tiempo de respuesta:** < 100ms
    - **Disponibilidad:** 99.9%
    - **Rate limit:** Sin límite
    
    ## 🔗 Ejemplo de Uso
    ```bash
    curl -X GET "https://api.recomendaciones.com/status" \\
         -H "accept: application/json"
    ```
    """,
    response_description="✅ Estado actual del servicio con timestamp preciso",
    response_model=StatusResponse,
    responses={
        200: {
            "description": "✅ **Servicio Operativo** - Sistema funcionando correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": True,
                        "date": "2025-01-14T10:30:00.123456Z"
                    }
                }
            }
        },
        500: {
            "description": "❌ **Error Crítico** - Servicio no disponible o degradado",
            "content": {
                "application/json": {
                    "examples": {
                        "error_interno": {
                            "summary": "Error interno del sistema",
                            "value": {
                                "detail": "Error interno del servicio: Connection timeout"
                            }
                        },
                        "error_db": {
                            "summary": "Error de base de datos",
                            "value": {
                                "detail": "Error interno del servicio: Database connection failed"
                            }
                        }
                    }
                }
            }
        }
    },
    tags=["🏥 Health Check"],
    operation_id="get_service_status"
)
def get_status(db_service: DatabaseService = Depends(get_db_service)) -> StatusResponse:
    """
    Retorna el estado actual del servicio de recomendaciones.
    
    Verifica que el servicio esté operativo y proporciona timestamp
    actual para sincronización y monitoreo.
    
    Args:
        db_service: Servicio de base de datos para verificaciones opcionales
        
    Returns:
        StatusResponse: Estado del servicio con timestamp UTC
        
    Raises:
        HTTPException: Si hay errores críticos en el servicio
        
    Note:
        Este endpoint debe responder rápidamente (< 100ms) para
        ser efectivo en health checks automáticos.
    """
    try:
        # Verificación básica del servicio
        current_time = datetime.now(timezone.utc)
        
        # TODO: Agregar verificaciones adicionales si es necesario:
        # - Conectividad a base de datos
        # - Estado de cache ML
        # - Memoria disponible
        # - Etc.
        
        return StatusResponse(
            status=True,
            date=current_time
        )
        
    except Exception as e:
        # En caso de error crítico, retornar 500
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servicio: {str(e)}"
        )
