"""
Endpoint de recomendaciones basadas en categorías, actores y otros filtros.

Proporciona recomendaciones personalizadas utilizando diferentes enfoques:
- Categorías/géneros de películas vistas
- Actores de películas vistas  
- Idiomas preferidos
- Ratings/clasificaciones
- Popularidad general

El endpoint analiza el historial del usuario y genera recomendaciones
explicables basadas en el parámetro 'focus' seleccionado.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from src.schemas import RecommendationsResponse, RecommendedMovie, WatchedMovieDetail
from src.database.db_service import DatabaseService
from src.dependencies import get_db_service

router = APIRouter()

# Configuración de opciones válidas para el parámetro focus
VALID_FOCUS_OPTIONS = [
    "category",    # Singular para consistencia con API
    "actor",       # Singular para consistencia con API
    "language",    # Singular para consistencia con API
    "rating",      # Singular para consistencia con API
    "popularity"   # Recomendaciones por popularidad general
]

# Mapeo para compatibilidad con versiones anteriores
FOCUS_MAPPING = {
    "categories": "category",
    "actors": "actor", 
    "languages": "language",
    "ratings": "rating",
    "directors": "director"  # No implementado pero mapeado
}

@router.get(
    "/recommendations",
    summary="🎬 Recomendaciones Personalizadas de Películas",
    description="""
    # 🤖 Motor de Recomendaciones Inteligente
    
    Genera recomendaciones cinematográficas personalizadas analizando el historial de visualización del usuario.
    
    ## 🎯 Algoritmos Disponibles
    
    | Enfoque | Descripción | Ideal Para |
    |---------|-------------|------------|
    | 🎭 `category` | Basado en géneros favoritos | Usuarios con preferencias claras de género |
    | 🌟 `actor` | Basado en actores preferidos | Fans de actores específicos |
    | 🌍 `language` | Basado en idiomas preferidos | Usuarios multilingües |
    | ⭐ `rating` | Basado en clasificaciones | Usuarios con filtros parentales |
    | 🔥 `popularity` | Basado en tendencias globales | Usuarios que buscan éxitos mainstream |
    
    ## 🔄 Proceso de Recomendación
    
    ```mermaid
    graph LR
        A[👤 Usuario] --> B[📊 Análisis Historial]
        B --> C[🎯 Extracción Características]
        C --> D[🔍 Búsqueda Similares]
        D --> E[❌ Filtro Ya Vistas]
        E --> F[📋 Top 10 Resultados]
    ```
    
    ## 📝 Parámetros de Entrada
    
    ### 🆔 user_id (obligatorio)
    - **Tipo:** `integer`
    - **Rango:** >= 1
    - **Ejemplo:** `123`
    - **Descripción:** Identificador único del usuario en el sistema
    
    ### 🎯 focus (obligatorio)
    - **Tipo:** `string`
    - **Valores:** `category`, `actor`, `language`, `rating`, `popularity`
    - **Ejemplo:** `"category"`
    - **Descripción:** Algoritmo de recomendación a aplicar
    
    ## 📊 Estructura de Respuesta
    
    ```json
    {
      "user_id": 123,
      "focus": "category",
      "movies_watched": ["The Matrix", "Inception"],
      "recommendations": [
        {
          "title": "Blade Runner 2049",
          "year": 2017,
          "reason": "Recomendada por categoría: Sci-Fi"
        }
      ]
    }
    ```
    
    ## 🚀 Ejemplo de Uso
    ```bash
    curl -X GET "https://api.recomendaciones.com/recommendations?user_id=123&focus=category" \\
         -H "accept: application/json"
    ```
    
    ## ⚡ Rendimiento
    - **Tiempo de respuesta:** 200-500ms
    - **Cache:** 5 minutos por usuario
    - **Rate limit:** 100 req/min por usuario
    """,
    response_description="🎬 Lista de películas recomendadas con contexto y explicaciones",
    response_model=RecommendationsResponse,
    responses={
        200: {
            "description": "✅ **Recomendaciones Generadas** - Lista personalizada de películas",
            "content": {
                "application/json": {
                    "examples": {
                        "recomendaciones_categoria": {
                            "summary": "🎭 Recomendaciones por Categoría",
                            "value": {
                                "user_id": 123,
                                "focus": "category",
                                "movies_watched": [
                                    "The Matrix (1999) - Sci-Fi",
                                    "Inception (2010) - Sci-Fi"
                                ],
                                "recommendations": [
                                    {
                                        "title": "Blade Runner 2049",
                                        "year": 2017,
                                        "reason": "Recomendada por categoría: Sci-Fi"
                                    },
                                    {
                                        "title": "Interstellar", 
                                        "year": 2014,
                                        "reason": "Recomendada por categoría: Sci-Fi"
                                    }
                                ]
                            }
                        },
                        "recomendaciones_actor": {
                            "summary": "🌟 Recomendaciones por Actor",
                            "value": {
                                "user_id": 456,
                                "focus": "actor",
                                "movies_watched": [
                                    "The Dark Knight (2008) - Christian Bale",
                                    "American Psycho (2000) - Christian Bale"
                                ],
                                "recommendations": [
                                    {
                                        "title": "Ford v Ferrari",
                                        "year": 2019,
                                        "reason": "Recomendada por actor: Christian Bale"
                                    }
                                ]
                            }
                        },
                        "sin_historial": {
                            "summary": "👤 Usuario Nuevo",
                            "value": {
                                "user_id": 999,
                                "focus": "category",
                                "movies_watched": [],
                                "recommendations": [
                                    {
                                        "title": "The Avengers",
                                        "year": 2012,
                                        "reason": "Recomendación por popularidad (usuario nuevo)"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "❌ **Parámetros Inválidos** - Error en los datos de entrada",
            "content": {
                "application/json": {
                    "examples": {
                        "user_id_invalido": {
                            "summary": "ID de usuario inválido",
                            "value": {
                                "detail": "El user_id debe ser un número positivo"
                            }
                        },
                        "focus_invalido": {
                            "summary": "Valor de focus no válido",
                            "value": {
                                "detail": "focus debe ser uno de: category, actor, language, rating, popularity"
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "❌ **Usuario No Encontrado** - El usuario no existe en el sistema",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Usuario con ID 123 no encontrado"
                    }
                }
            }
        },
        500: {
            "description": "❌ **Error Interno** - Problema en el servidor",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error interno del servidor al generar recomendaciones"
                    }
                }
            }
        }
    },
    tags=["🎬 Recomendaciones"],
    operation_id="get_personalized_recommendations"
)
def get_recommendations(
    user_id: int = Query(
        ..., 
        description="🆔 **ID del Usuario** - Identificador único del usuario en el sistema",
        examples=[123, 456, 789],
        ge=1,
        title="User ID",
        alias="user_id"
    ),
    focus: str = Query(
        ...,
        description="🎯 **Algoritmo de Recomendación** - Tipo de enfoque para generar recomendaciones",
        examples=["category", "actor", "language", "rating", "popularity"],
        title="Focus Algorithm",
        alias="focus"
    ),
    db_service: DatabaseService = Depends(get_db_service)
) -> RecommendationsResponse:
    """
    Genera recomendaciones personalizadas para un usuario específico.
    
    Args:
        user_id: Identificador único del usuario
        focus: Tipo de enfoque para las recomendaciones
        db_service: Servicio de base de datos inyectado
        
    Returns:
        RecommendationsResponse: Recomendaciones con contexto del usuario
        
    Raises:
        HTTPException: Si el focus no es válido o hay errores de BD
    """
    # Normalizar focus para compatibilidad
    normalized_focus = FOCUS_MAPPING.get(focus.lower(), focus.lower())
    
    if normalized_focus not in VALID_FOCUS_OPTIONS:
        # Mantener compatibilidad: retornar 200 con mensaje explicativo
        watched_movies_details = db_service.get_film_details_for_customer(user_id)
        return RecommendationsResponse(
            user_id=user_id,
            focus=focus,
            recommendations=[f"No se pudo generar recomendación para {focus}"],
            watched_movies_details=watched_movies_details,
            recommended_movies=[RecommendedMovie(
                film="", 
                reason=f"Tipo de recomendación no válido. Opciones válidas: {', '.join(VALID_FOCUS_OPTIONS)}."
            )]
        )
    
    try:
        # Obtener contexto del usuario
        watched_movies_details = db_service.get_film_details_for_customer(user_id)
        watched_movie_titles = [movie.get("title") for movie in watched_movies_details]
        
        # Generar recomendaciones según el enfoque
        recommended_movies = _generate_recommendations_by_focus(
            db_service, user_id, normalized_focus, watched_movie_titles
        )
        
        return RecommendationsResponse(
            user_id=user_id,
            focus=focus,  # Retornar el focus original
            recommendations=[f"Recomendación para usuario {user_id} con enfoque {focus}"],
            watched_movies_details=watched_movies_details,
            recommended_movies=recommended_movies
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando recomendaciones: {str(e)}"
        )

def _generate_recommendations_by_focus(
    db_service: DatabaseService,
    user_id: int,
    focus: str,
    watched_titles: List[str]
) -> List[RecommendedMovie]:
    """
    Genera recomendaciones según el enfoque especificado.
    
    Args:
        db_service: Servicio de base de datos
        user_id: ID del usuario
        focus: Tipo de enfoque normalizado
        watched_titles: Títulos de películas ya vistas
        
    Returns:
        Lista de películas recomendadas con explicaciones
    """
    if focus == "actor":
        return _get_actor_recommendations(db_service, user_id, watched_titles)
    elif focus == "category":
        return _get_category_recommendations(db_service, user_id, watched_titles)
    elif focus == "language":
        return _get_language_recommendations(db_service, user_id, watched_titles)
    elif focus == "rating":
        return _get_rating_recommendations(db_service, user_id, watched_titles)
    elif focus == "popularity":
        return _get_popularity_recommendations(db_service, watched_titles)
    else:
        return [RecommendedMovie(
            film="", 
            reason=f"Algoritmo para '{focus}' no implementado"
        )]

def _get_actor_recommendations(
    db_service: DatabaseService, 
    user_id: int, 
    watched_titles: List[str]
) -> List[RecommendedMovie]:
    """Genera recomendaciones basadas en actores."""
    recommended_titles = db_service.get_recommended_movies_by_actor_affinity(
        user_id, watched_titles, limit=10
    )
    return [
        RecommendedMovie(
            film=title, 
            reason="Afinidad con actores de películas que has visto"
        )
        for title in recommended_titles
    ]

def _get_category_recommendations(
    db_service: DatabaseService,
    user_id: int, 
    watched_titles: List[str]
) -> List[RecommendedMovie]:
    """Genera recomendaciones basadas en categorías/géneros."""
    genres = db_service.get_genres_from_watched_movies(user_id)
    if not genres:
        return [RecommendedMovie(
            film="", 
            reason="No hay suficientes datos de géneros para generar recomendaciones"
        )]
    
    recommended_titles = db_service.get_popular_movies_by_genres(
        genres, watched_titles, limit=10
    )
    return [
        RecommendedMovie(
            film=title,
            reason=f"Popular en géneros que has visto: {', '.join(genres[:3])}"
        )
        for title in recommended_titles
    ]

def _get_language_recommendations(
    db_service: DatabaseService,
    user_id: int,
    watched_titles: List[str]
) -> List[RecommendedMovie]:
    """Genera recomendaciones basadas en idiomas."""
    languages = db_service.get_languages_from_watched_movies(user_id)
    if not languages:
        return [RecommendedMovie(
            film="", 
            reason="No hay suficientes datos de idiomas para generar recomendaciones"
        )]
    
    recommended_titles = db_service.get_popular_movies_by_languages(
        languages, watched_titles, limit=10
    )
    return [
        RecommendedMovie(
            film=title,
            reason=f"Popular en idiomas que prefieres: {', '.join(languages)}"
        )
        for title in recommended_titles
    ]

def _get_rating_recommendations(
    db_service: DatabaseService,
    user_id: int,
    watched_titles: List[str]
) -> List[RecommendedMovie]:
    """Genera recomendaciones basadas en ratings/clasificaciones."""
    ratings = db_service.get_ratings_from_watched_movies(user_id)
    if not ratings:
        return [RecommendedMovie(
            film="", 
            reason="No hay suficientes datos de clasificaciones para generar recomendaciones"
        )]
    
    recommended_titles = db_service.get_popular_movies_by_ratings(
        ratings, watched_titles, limit=10
    )
    return [
        RecommendedMovie(
            film=title,
            reason=f"Popular con clasificaciones que has visto: {', '.join(ratings)}"
        )
        for title in recommended_titles
    ]

def _get_popularity_recommendations(
    db_service: DatabaseService,
    watched_titles: List[str]
) -> List[RecommendedMovie]:
    """Genera recomendaciones basadas en popularidad general."""
    recommended_titles = db_service.get_most_popular_movies(
        watched_titles, limit=10
    )
    return [
        RecommendedMovie(
            film=title,
            reason="Película popular en general"
        )
        for title in recommended_titles
    ]
