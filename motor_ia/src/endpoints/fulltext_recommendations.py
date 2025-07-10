"""
Endpoint de recomendaciones basadas en análisis de texto completo (fulltext).

Utiliza el campo 'fulltext' de PostgreSQL para analizar patrones semánticos
en las descripciones de películas vistas por el usuario y generar recomendaciones
basadas en similitud de contenido textual.

Algoritmo:
1. Extrae datos fulltext de películas vistas por el usuario
2. Analiza y agrega preferencias por palabras clave
3. Busca películas con palabras clave similares usando ts_rank
4. Aplica diversificación para evitar recomendaciones repetitivas
5. Retorna top 10 recomendaciones con explicaciones detalladas
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Set
from src.schemas import RecommendationsResponse, RecommendedMovie, WatchedMovieDetail
from src.database.db_service import DatabaseService
from src.dependencies import get_db_service

router = APIRouter()

# Configuración del algoritmo de diversificación
MAX_RECOMMENDATIONS_PER_KEYWORD = 3
TOTAL_RECOMMENDATIONS_LIMIT = 10
CANDIDATE_EXPANSION_FACTOR = 5  # Buscar 5x más candidatos para diversificar

@router.get(
    "/fulltext-recommendations",
    summary="🔍 Recomendaciones por Análisis Semántico",
    description="""
    # 🧠 Motor de Análisis Textual Avanzado
    
    Sistema de recomendaciones que utiliza análisis semántico profundo del contenido textual de las películas.
    
    ## 🎯 Tecnología Utilizada
    
    | Componente | Tecnología | Descripción |
    |------------|------------|-------------|
    | 🔍 **Búsqueda Textual** | PostgreSQL Full-Text Search | ts_rank, tsvector, tsquery |
    | 🧮 **Análisis Semántico** | Procesamiento de lenguaje natural | Extracción de palabras clave |
    | 🎲 **Diversificación** | Algoritmo personalizado | Evita recomendaciones monótonas |
    | ⚖️ **Balanceado** | Distribución inteligente | Max 3 por palabra clave |
    
    ## 🔄 Proceso de Análisis
    
    ```mermaid
    graph TD
        A[👤 Usuario] --> B[📊 Extracción Fulltext]
        B --> C[🔤 Análisis Palabras Clave]
        C --> D[🔍 Búsqueda ts_rank]
        D --> E[🎲 Diversificación]
        E --> F[📋 Top 10 Balanceadas]
    ```
    
    ## 🎬 Tipos de Análisis
    
    ### 📝 Descripción Textual
    - **Tramas y argumentos** de películas vistas
    - **Temas recurrentes** identificados
    - **Estilos narrativos** preferidos
    
    ### 🏷️ Palabras Clave Extraídas
    - **Géneros específicos** (thriller psicológico, comedia romántica)
    - **Ambientaciones** (espacio, época victoriana, futuro)
    - **Elementos temáticos** (venganza, amistad, supervivencia)
    
    ## ⚡ Configuración del Algoritmo
    
    | Parámetro | Valor | Propósito |
    |-----------|-------|-----------|
    | **Recomendaciones por palabra clave** | Máx. 3 | Diversificación temática |
    | **Total de recomendaciones** | 10 | Balance cantidad/calidad |
    | **Factor de expansión** | 5x | Amplitud de candidatos |
    
    ## 🚀 Ejemplo de Uso
    ```bash
    curl -X GET "https://api.recomendaciones.com/fulltext-recommendations?user_id=123" \\
         -H "accept: application/json"
    ```
    
    ## 💡 Ventajas del Enfoque
    - ✅ **Granularidad:** Más específico que géneros o actores
    - ✅ **Semántica:** Captura preferencias temáticas sutiles  
    - ✅ **Nativo:** Usa capacidades PostgreSQL optimizadas
    - ✅ **Diverso:** Algoritmo anti-monotonía integrado
    """,
    response_description="🎭 Recomendaciones basadas en similitud semántica con diversificación inteligente",
    response_model=RecommendationsResponse,
    responses={
        200: {
            "description": "✅ **Análisis Completado** - Recomendaciones generadas por análisis textual",
            "content": {
                "application/json": {
                    "examples": {
                        "analisis_exitoso": {
                            "summary": "🎬 Análisis con diversificación",
                            "value": {
                                "user_id": 123,
                                "focus": "fulltext",
                                "movies_watched": [
                                    "Inception (2010) - Sci-fi psychological thriller with complex narrative",
                                    "Memento (2000) - Neo-noir psychological thriller with memory themes"
                                ],
                                "recommendations": [
                                    {
                                        "title": "Shutter Island",
                                        "year": 2010,
                                        "reason": "Recomendada por similitud textual: psychological, thriller, complex"
                                    },
                                    {
                                        "title": "The Prestige",
                                        "year": 2006,
                                        "reason": "Recomendada por similitud textual: narrative, mystery, psychological"
                                    },
                                    {
                                        "title": "Donnie Darko",
                                        "year": 2001,
                                        "reason": "Recomendada por similitud textual: complex, psychological, sci-fi"
                                    }
                                ]
                            }
                        },
                        "usuario_nuevo": {
                            "summary": "👤 Usuario sin historial",
                            "value": {
                                "user_id": 999,
                                "focus": "fulltext", 
                                "movies_watched": [],
                                "recommendations": [
                                    {
                                        "title": "The Shawshank Redemption",
                                        "year": 1994,
                                        "reason": "Recomendación por popularidad (usuario sin historial textual)"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "❌ **Usuario No Encontrado** - El usuario no existe o no tiene datos",
            "content": {
                "application/json": {
                    "examples": {
                        "usuario_inexistente": {
                            "summary": "Usuario no registrado",
                            "value": {
                                "detail": "Usuario con ID 123 no encontrado"
                            }
                        },
                        "sin_datos_fulltext": {
                            "summary": "Sin datos de texto",
                            "value": {
                                "detail": "No hay datos de fulltext disponibles para el usuario 123"
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "❌ **Error Interno** - Error en el análisis textual o base de datos",
            "content": {
                "application/json": {
                    "examples": {
                        "error_analisis": {
                            "summary": "Error en análisis semántico",
                            "value": {
                                "detail": "Error en el análisis de texto completo: syntax error in tsquery"
                            }
                        },
                        "error_bd": {
                            "summary": "Error de base de datos",
                            "value": {
                                "detail": "Error interno del servidor: connection timeout"
                            }
                        }
                    }
                }
            }
        }
    },
    tags=["🔍 Análisis Textual"],
    operation_id="get_fulltext_recommendations"
)
def get_fulltext_recommendations(
    user_id: int = Query(
        ...,
        description="🆔 **ID del Usuario** - Identificador para análisis semántico personalizado",
        examples=[123, 456, 789],
        ge=1,
        title="User ID",
        alias="user_id"
    ),
    db_service: DatabaseService = Depends(get_db_service)
) -> RecommendationsResponse:
    """
    Genera recomendaciones basadas en análisis de texto completo.
    
    Args:
        user_id: Identificador único del usuario
        db_service: Servicio de base de datos inyectado
        
    Returns:
        RecommendationsResponse: Recomendaciones con análisis textual
        
    Raises:
        HTTPException: Si hay errores en el procesamiento o BD
    """
    try:
        # Obtener contexto del usuario
        watched_movies_details = db_service.get_film_details_for_customer(user_id)
        watched_movie_titles = [movie.get("title") for movie in watched_movies_details]
        
        if not watched_movies_details:
            return _create_empty_response(user_id, "Usuario no encontrado o sin historial")
        
        # Análisis de preferencias textuales
        fulltext_data = db_service.get_fulltext_data_for_customer(user_id)
        user_preferred_types = db_service.analyze_fulltext_preferences(fulltext_data)
        
        if not user_preferred_types:
            return _create_empty_response(user_id, "No hay suficientes datos de fulltext para generar recomendaciones")
        
        # Generar recomendaciones diversificadas
        recommended_movies = _generate_diversified_recommendations(
            db_service, user_preferred_types, watched_movie_titles
        )
        
        return RecommendationsResponse(
            user_id=user_id,
            focus="fulltext",
            recommendations=["Recomendación basada en análisis de texto completo"],
            watched_movies_details=watched_movies_details,
            recommended_movies=recommended_movies
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando recomendaciones fulltext: {str(e)}"
        )

def _create_empty_response(user_id: int, reason: str) -> RecommendationsResponse:
    """
    Crea respuesta vacía con mensaje explicativo.
    
    Args:
        user_id: ID del usuario
        reason: Motivo de la respuesta vacía
        
    Returns:
        RecommendationsResponse con mensaje explicativo
    """
    return RecommendationsResponse(
        user_id=user_id,
        focus="fulltext",
        recommendations=["Sin recomendaciones disponibles"],
        watched_movies_details=[],
        recommended_movies=[RecommendedMovie(film="", reason=reason)]
    )

def _generate_diversified_recommendations(
    db_service: DatabaseService,
    user_preferred_types: Dict[str, int],
    watched_titles: List[str]
) -> List[RecommendedMovie]:
    """
    Genera recomendaciones diversificadas basadas en preferencias textuales.
    
    Aplica algoritmo de diversificación para evitar que todas las recomendaciones
    sean del mismo tipo/género y proporcionar variedad al usuario.
    
    Args:
        db_service: Servicio de base de datos
        user_preferred_types: Palabras clave preferidas con puntajes
        watched_titles: Títulos ya vistos (para exclusión)
        
    Returns:
        Lista diversificada de recomendaciones con explicaciones
    """
    # Expandir búsqueda para tener suficientes candidatos
    expanded_limit = TOTAL_RECOMMENDATIONS_LIMIT * CANDIDATE_EXPANSION_FACTOR
    potential_movies = db_service.get_movies_by_fulltext_affinity(
        user_preferred_types, watched_titles, limit=expanded_limit
    )
    
    if not potential_movies:
        return [RecommendedMovie(
            film="", 
            reason="No se encontraron películas similares en la base de datos"
        )]
    
    # Aplicar algoritmo de diversificación
    return _apply_diversification_algorithm(
        db_service, potential_movies, user_preferred_types
    )

def _apply_diversification_algorithm(
    db_service: DatabaseService,
    potential_movies: List[Dict[str, str]],
    user_preferred_types: Dict[str, int]
) -> List[RecommendedMovie]:
    """
    Aplica algoritmo de diversificación para seleccionar recomendaciones variadas.
    
    Args:
        db_service: Servicio de base de datos
        potential_movies: Lista de películas candidatas
        user_preferred_types: Preferencias del usuario por palabra clave
        
    Returns:
        Lista diversificada de recomendaciones
    """
    # Ordenar palabras clave por relevancia
    sorted_keywords = sorted(
        user_preferred_types.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    final_recommendations: List[RecommendedMovie] = []
    recommended_titles: Set[str] = set()
    keyword_counts: Dict[str, int] = {}
    
    # Iterar por palabras clave en orden de relevancia
    for keyword, score in sorted_keywords:
        if len(final_recommendations) >= TOTAL_RECOMMENDATIONS_LIMIT:
            break
            
        keyword_recommendations = _get_recommendations_for_keyword(
            db_service, potential_movies, keyword, recommended_titles, keyword_counts
        )
        
        final_recommendations.extend(keyword_recommendations)
        
        # Actualizar conjuntos de control
        for rec in keyword_recommendations:
            recommended_titles.add(rec.film)
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    return final_recommendations[:TOTAL_RECOMMENDATIONS_LIMIT]

def _get_recommendations_for_keyword(
    db_service: DatabaseService,
    potential_movies: List[Dict[str, str]],
    keyword: str,
    recommended_titles: Set[str],
    keyword_counts: Dict[str, int]
) -> List[RecommendedMovie]:
    """
    Obtiene recomendaciones para una palabra clave específica.
    
    Args:
        db_service: Servicio de base de datos
        potential_movies: Películas candidatas
        keyword: Palabra clave actual
        recommended_titles: Títulos ya recomendados
        keyword_counts: Contador de recomendaciones por palabra clave
        
    Returns:
        Lista de recomendaciones para esta palabra clave
    """
    recommendations: List[RecommendedMovie] = []
    current_keyword_count = keyword_counts.get(keyword, 0)
    
    if current_keyword_count >= MAX_RECOMMENDATIONS_PER_KEYWORD:
        return recommendations
    
    for movie_data in potential_movies:
        if len(recommendations) >= MAX_RECOMMENDATIONS_PER_KEYWORD - current_keyword_count:
            break
            
        movie_title = movie_data["title"]
        movie_fulltext = movie_data["fulltext"]
        
        # Verificar si ya fue recomendada
        if movie_title in recommended_titles:
            continue
            
        # Verificar si la película contiene la palabra clave
        parsed_fulltext = db_service._parse_fulltext_string(movie_fulltext)
        if keyword in parsed_fulltext:
            recommendations.append(RecommendedMovie(
                film=movie_title,
                reason=f"Afinidad con el tema '{keyword}' (puntuación: {parsed_fulltext[keyword]})"
            ))
    
    return recommendations
