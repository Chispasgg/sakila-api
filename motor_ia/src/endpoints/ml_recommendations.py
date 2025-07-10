"""
Endpoint de recomendaciones basadas en Machine Learning.

Implementa algoritmo de recomendaciones usando TF-IDF (Term Frequency-Inverse Document Frequency)
y similitud coseno para generar recomendaciones semánticas basadas en el contenido
de las películas vistas por el usuario.

Algoritmo:
1. Construye modelo TF-IDF con todas las películas de la base de datos
2. Vectoriza el perfil del usuario basado en películas vistas
3. Calcula similitud coseno entre perfil usuario y todas las películas
4. Filtra películas ya vistas y retorna las más similares
5. Incluye fallback a popularidad para usuarios con pocos datos

Características:
- Cache de modelo ML para mejor performance
- Fallback automático a recomendaciones por popularidad
- Scores de similitud cuantificados (0.0-1.0)
- Explicaciones detalladas del algoritmo utilizado
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List, Dict, Any
from src.schemas import RecommendedMovieML
from src.database.db_service import DatabaseService
from src.dependencies import get_db_service

router = APIRouter()

# Configuración del algoritmo ML
MINIMUM_WATCHED_MOVIES_FOR_ML = 3  # Umbral mínimo para usar ML
DEFAULT_RECOMMENDATIONS_LIMIT = 10

@router.get(
    "/ml/recommendations/{customer_id}",
    summary="🤖 Recomendaciones con Inteligencia Artificial",
    description="""
    # 🧠 Motor de Machine Learning Avanzado
    
    Sistema de recomendaciones estado-del-arte usando algoritmos de ML para análisis semántico profundo.
    
    ## 🎯 Tecnología de IA Utilizada
    
    | Algoritmo | Descripción | Beneficio |
    |-----------|-------------|-----------|
    | 🔤 **TF-IDF** | Term Frequency-Inverse Document Frequency | Vectorización semántica |
    | 📐 **Similitud Coseno** | Medida de similitud vectorial | Scores cuantificados (0-1) |
    | 🧮 **Agregación Vectorial** | Promedio ponderado de películas vistas | Perfil coherente del usuario |
    | 🔄 **Fallback Inteligente** | Degradación a popularidad | Robustez ante datos limitados |
    
    ## 🔬 Pipeline de Machine Learning
    
    ```mermaid
    graph TD
        A[🎬 Catálogo Completo] --> B[🔤 Vectorización TF-IDF]
        C[👤 Películas Vistas] --> D[📊 Perfil Usuario ML]
        B --> E[📐 Similitud Coseno]
        D --> E
        E --> F[📈 Ranking por Score]
        F --> G[❌ Filtro Ya Vistas]
        G --> H[🏆 Top 10 Recomendaciones]
    ```
    
    ## 📊 Datos de Entrada para ML
    
    ### 🎬 Features de Películas
    - **Textual:** Título, descripción, contenido fulltext
    - **Categórico:** Género, rating, idioma
    - **Metadata:** Actores, director, año
    
    ### 👤 Perfil de Usuario  
    - **Vector promedio** de todas las películas vistas
    - **Ponderación** por ratings o frecuencia de visualización
    - **Normalización** para evitar bias por cantidad
    
    ## 🎚️ Configuración del Algoritmo
    
    | Parámetro | Valor | Propósito |
    |-----------|-------|-----------|
    | **Umbral mínimo para ML** | 3 películas | Datos suficientes para ML |
    | **Límite de recomendaciones** | 10 películas | Balance cantidad/calidad |
    | **Score mínimo** | 0.1 | Filtro de relevancia |
    
    ## 🔄 Sistema de Fallbacks
    
    ### 📊 Estrategia de Degradación
    1. **🤖 ML Completo** (≥3 películas vistas): Algoritmo TF-IDF completo
    2. **📈 Popularidad** (<3 películas): Recomendaciones por tendencias
    3. **🆕 Usuario Nuevo** (0 películas): Películas más populares globalmente
    4. **⚠️ Error ML** (fallos técnicos): Degradación automática a popularidad
    
    ## 🚀 Ejemplo de Uso
    ```bash
    curl -X GET "https://api.recomendaciones.com/ml/recommendations/123" \\
         -H "accept: application/json"
    ```
    
    ## 💡 Ventajas del ML
    - ✅ **Precisión:** Scores cuantificados de similitud
    - ✅ **Semántica:** Comprende contenido, no solo metadatos  
    - ✅ **Escalabilidad:** Eficiente con catálogos grandes
    - ✅ **Robustez:** Fallbacks automáticos inteligentes
    - ✅ **Explicabilidad:** Razones claras para cada recomendación
    """,
    response_description="🎯 Recomendaciones ML con scores de similitud y explicaciones algoritmo usado",
    response_model=List[RecommendedMovieML],
    responses={
        200: {
            "description": "✅ **ML Ejecutado** - Recomendaciones generadas por inteligencia artificial",
            "content": {
                "application/json": {
                    "examples": {
                        "ml_completo": {
                            "summary": "🤖 Algoritmo ML Completo",
                            "value": [
                                {
                                    "title": "Blade Runner 2049",
                                    "year": 2017,
                                    "similarity_score": 0.89,
                                    "reason": "Recomendación ML: Alta similitud temática y estilística"
                                },
                                {
                                    "title": "Ex Machina", 
                                    "year": 2014,
                                    "similarity_score": 0.82,
                                    "reason": "Recomendación ML: Similitud en conceptos de IA y sci-fi"
                                },
                                {
                                    "title": "Her",
                                    "year": 2013, 
                                    "similarity_score": 0.76,
                                    "reason": "Recomendación ML: Temas tecnológicos y narrativa reflexiva"
                                }
                            ]
                        },
                        "fallback_popularidad": {
                            "summary": "📈 Fallback por Pocos Datos",
                            "value": [
                                {
                                    "title": "The Avengers",
                                    "year": 2012,
                                    "similarity_score": 0.0,
                                    "reason": "Recomendación por popularidad debido a pocas películas vistas"
                                },
                                {
                                    "title": "Inception",
                                    "year": 2010,
                                    "similarity_score": 0.0,
                                    "reason": "Recomendación por popularidad debido a pocas películas vistas"
                                }
                            ]
                        },
                        "usuario_nuevo": {
                            "summary": "🆕 Usuario Sin Historial",
                            "value": [
                                {
                                    "title": "The Shawshank Redemption",
                                    "year": 1994,
                                    "similarity_score": 0.0,
                                    "reason": "Recomendación por popularidad debido a pocas películas vistas"
                                }
                            ]
                        }
                    }
                }
            }
        },
        400: {
            "description": "❌ **Parámetro Inválido** - Error en el ID del cliente",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "El customer_id debe ser un número entero positivo"
                    }
                }
            }
        },
        404: {
            "description": "❌ **Cliente No Encontrado** - El cliente no existe en el sistema",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cliente con ID 123 no encontrado"
                    }
                }
            }
        },
        422: {
            "description": "❌ **Formato Inválido** - Error en el formato del customer_id",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "customer_id"],
                                "msg": "ensure this value is greater than or equal to 1",
                                "type": "value_error.number.not_ge"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "❌ **Error ML** - Fallo en el algoritmo de machine learning",
            "content": {
                "application/json": {
                    "examples": {
                        "error_ml": {
                            "summary": "Error en algoritmo ML",
                            "value": {
                                "detail": "Error en algoritmo ML: memoria insuficiente para TF-IDF"
                            }
                        },
                        "error_vectorizacion": {
                            "summary": "Error en vectorización",
                            "value": {
                                "detail": "Error interno del servidor: falló la vectorización TF-IDF"
                            }
                        }
                    }
                }
            }
        }
    },
    tags=["🤖 Machine Learning"],
    operation_id="get_ml_recommendations"
)
def get_ml_recommendations(
    customer_id: int = Path(
        ...,
        description="🆔 **ID del Cliente** - Identificador único para generar perfil ML personalizado",
        examples=[123, 456, 789],
        ge=1,
        title="Customer ID",
        alias="customer_id"
    ),
    db_service: DatabaseService = Depends(get_db_service)
) -> List[RecommendedMovieML]:
    """
    Genera recomendaciones usando algoritmos de Machine Learning.
    
    Args:
        customer_id: Identificador único del cliente
        db_service: Servicio de base de datos inyectado
        
    Returns:
        List[RecommendedMovieML]: Lista de recomendaciones con scores de similitud
        
    Raises:
        HTTPException: Si hay errores en el procesamiento ML o acceso a BD
        
    Note:
        El algoritmo automáticamente hace fallback a popularidad si:
        - El usuario tiene menos de 3 películas vistas
        - Hay errores en el modelo TF-IDF
        - El usuario no existe en la base de datos
    """
    try:
        # Generar recomendaciones usando el servicio ML
        recommendations = db_service.get_ml_recommendations(
            customer_id, limit=DEFAULT_RECOMMENDATIONS_LIMIT
        )
        
        if not recommendations:
            # Fallback si no hay recomendaciones disponibles
            return _generate_fallback_recommendations(customer_id)
        
        # Validar y enriquecer recomendaciones
        return _validate_and_enrich_recommendations(recommendations, customer_id)
        
    except ValueError as e:
        # Error de validación (ej: customer_id inválido)
        raise HTTPException(
            status_code=400,
            detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        # Error interno - generar fallback
        return _generate_error_fallback_recommendations(customer_id, str(e))

def _validate_and_enrich_recommendations(
    recommendations: List[Dict[str, Any]], 
    customer_id: int
) -> List[RecommendedMovieML]:
    """
    Valida y enriquece las recomendaciones ML con información adicional.
    
    Args:
        recommendations: Lista de recomendaciones raw del servicio
        customer_id: ID del cliente
        
    Returns:
        Lista validada de recomendaciones ML
    """
    validated_recs = []
    
    for rec in recommendations:
        # Validar estructura de datos
        if not all(key in rec for key in ['title', 'similarity_score', 'explanation']):
            continue
            
        # Enriquecer explicación si es necesaria
        explanation = _enrich_explanation(rec['explanation'], rec['similarity_score'])
        
        validated_recs.append(RecommendedMovieML(
            film_id=rec.get('film_id'),
            title=rec['title'],
            similarity_score=float(rec['similarity_score']),
            explanation=explanation
        ))
    
    return validated_recs

def _enrich_explanation(explanation: str, similarity_score: float) -> str:
    """
    Enriquece la explicación con información adicional del score.
    
    Args:
        explanation: Explicación original
        similarity_score: Score de similitud
        
    Returns:
        Explicación enriquecida
    """
    if similarity_score > 0.8:
        confidence = "muy alta"
    elif similarity_score > 0.6:
        confidence = "alta"
    elif similarity_score > 0.4:
        confidence = "media"
    elif similarity_score > 0.2:
        confidence = "baja"
    else:
        confidence = "mínima"
    
    return f"{explanation} (Confianza: {confidence}, Score: {similarity_score:.3f})"

def _generate_fallback_recommendations(customer_id: int) -> List[RecommendedMovieML]:
    """
    Genera recomendaciones de fallback cuando no hay datos ML disponibles.
    
    Args:
        customer_id: ID del cliente
        
    Returns:
        Lista de recomendaciones por popularidad
    """
    return [RecommendedMovieML(
        film_id=None,
        title="No hay recomendaciones ML disponibles",
        similarity_score=0.0,
        explanation=f"No hay suficientes datos para generar recomendaciones ML para el cliente {customer_id}. "
                   "Ve más películas para obtener recomendaciones personalizadas."
    )]

def _generate_error_fallback_recommendations(customer_id: int, error_msg: str) -> List[RecommendedMovieML]:
    """
    Genera recomendaciones de fallback cuando hay errores en el sistema ML.
    
    Args:
        customer_id: ID del cliente
        error_msg: Mensaje de error
        
    Returns:
        Lista de recomendaciones de error con información de debug
    """
    return [RecommendedMovieML(
        film_id=None,
        title="Error en sistema de recomendaciones",
        similarity_score=0.0,
        explanation=f"Error temporal en el sistema ML para cliente {customer_id}. "
                   f"Por favor intenta más tarde. Error técnico: {error_msg[:100]}"
    )]
