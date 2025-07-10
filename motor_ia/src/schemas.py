"""
Esquemas de datos (modelos Pydant    film: str = Field(
        description="Título de la película recomendada",
        examples=["The Shawshank Redemption"]
    )
    reason: str = Field(
        description="Explicación algorítmica de por qué se recomienda esta película",
        examples=["Popular en un género que has visto"]
    ) la API de recomendaciones.

Define todas las estructuras de datos de entrada y salida utilizadas
por los endpoints de la API, proporcionando validación automática
y documentación de la API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StatusResponse(BaseModel):
    """
    ✅ Respuesta del Health Check del servicio.
    
    Indica el estado operativo actual del sistema de recomendaciones
    junto con un timestamp preciso para sincronización.
    
    Attributes:
        status: Estado booleano del servicio (True = operativo)
        date: Timestamp UTC preciso en formato ISO 8601
    """
    status: bool = Field(
        description="🟢 **Estado Operativo** - Indica si el servicio está funcionando correctamente",
        examples=[True, False]
    )
    date: datetime = Field(
        description="🕒 **Timestamp UTC** - Momento exacto de la respuesta en formato ISO 8601",
        examples=["2025-01-14T10:30:00.123456Z", "2025-01-14T15:45:30.789012Z"]
    )

class RecommendedMovie(BaseModel):
    """
    🎬 Película individual recomendada por el sistema.
    
    Representa una sola recomendación de película con título
    y explicación algorítmica del motivo de la recomendación.
    
    Attributes:
        film: Título completo de la película recomendada
        reason: Explicación técnica y entendible del algoritmo usado
    """
    film: str = Field(
        description="🎭 **Título de la Película** - Nombre completo de la película recomendada",
        examples=[
            "The Shawshank Redemption",
            "Pulp Fiction", 
            "The Dark Knight",
            "Forrest Gump"
        ]
    )
    reason: str = Field(
        description="🧠 **Explicación Algorítmica** - Motivo detallado de por qué se recomienda esta película",
        examples=[
            "Recomendada por categoría: Drama",
            "Recomendada por actor: Tom Hanks",
            "Recomendación ML: Alta similitud temática",
            "Recomendada por similitud textual: psychological, thriller"
        ]
    )

class WatchedMovieDetail(BaseModel):
    """
    📊 Detalles completos de película vista por el usuario.
    
    Contiene información integral sobre películas del historial
    del usuario, utilizada para análisis de preferencias y 
    generación de recomendaciones personalizadas.
    
    Attributes:
        title: Título oficial de la película
        rental_duration: Duración estándar del alquiler en días
        rental_rate: Precio de alquiler en moneda local
        fulltext: Contenido vectorizado para análisis semántico
        actors: Lista de actores principales del reparto
    """
    title: str = Field(
        description="🎭 **Título de la Película** - Nombre oficial y completo",
        examples=["Inception", "The Matrix", "Pulp Fiction", "Interstellar"]
    )
    rental_duration: int = Field(
        description="📅 **Duración del Alquiler** - Días estándar de alquiler",
        examples=[3, 5, 7],
        ge=1,
        le=30
    )
    rental_rate: float = Field(
        description="💰 **Precio de Alquiler** - Coste en moneda local",
        examples=[2.99, 4.99, 1.99, 3.49],
        ge=0,
        le=50.0
    )
    fulltext: str = Field(
        description="🔍 **Contenido Fulltext** - Texto vectorizado para análisis semántico PostgreSQL",
        examples=[
            "'action':1 'thriller':2 'sci-fi':1",
            "'drama':3 'family':1 'emotional':2",
            "'comedy':2 'romance':1 'light':1"
        ]
    )
    actors: List[str] = Field(
        description="🌟 **Reparto Principal** - Lista de actores protagonistas",
        examples=[
            ["Leonardo DiCaprio", "Marion Cotillard"],
            ["Keanu Reeves", "Laurence Fishburne"],
            ["John Travolta", "Samuel L. Jackson"],
            ["Matthew McConaughey", "Anne Hathaway"]
        ]
    )

class RecommendationsResponse(BaseModel):
    """
    📋 Respuesta completa del sistema de recomendaciones.
    
    Estructura integral que incluye las recomendaciones generadas
    junto con el contexto completo del usuario para transparencia
    y explicabilidad del algoritmo.
    
    Attributes:
        user_id: Identificador del usuario objetivo
        focus: Algoritmo de recomendación utilizado
        recommendations: Lista interna de IDs (legacy)
        watched_movies_details: Contexto del historial del usuario
        recommended_movies: Lista final de películas recomendadas
    """
    user_id: int = Field(
        description="🆔 **ID del Usuario** - Identificador único del usuario objetivo",
        examples=[123, 456, 789],
        ge=1
    )
    focus: str = Field(
        description="🎯 **Algoritmo Utilizado** - Tipo de recomendación aplicada",
        examples=["category", "actor", "language", "rating", "popularity", "fulltext"]
    )
    recommendations: List[str] = Field(
        description="🔧 **IDs Internos** - Lista interna de identificadores (legacy)",
        examples=[["rec_1", "rec_2", "rec_3"], ["popular_1", "popular_2"]]
    )
    watched_movies_details: List[WatchedMovieDetail] = Field(
        description="📚 **Historial del Usuario** - Contexto detallado de películas vistas",
        examples=[
            [],  # Usuario nuevo
            [{"title": "Inception", "rental_duration": 3, "rental_rate": 4.99}]  # Con historial
        ]
    )
    recommended_movies: List[RecommendedMovie] = Field(
        description="🎬 **Recomendaciones Finales** - Lista de películas sugeridas con explicaciones",
        examples=[
            [],  # Sin recomendaciones
            [{"film": "The Matrix", "reason": "Recomendada por categoría: Sci-Fi"}]
        ]
    )

class RecommendedMovieML(BaseModel):
    """
    🤖 Recomendación generada por Machine Learning.
    
    Modelo especializado para recomendaciones ML que incluye
    métricas cuantificadas de similitud y explicaciones
    técnicas del algoritmo utilizado.
    
    Attributes:
        film_id: ID de la película (null para fallbacks)
        title: Título completo de la película
        similarity_score: Score de similitud semántica (0.0-1.0)
        explanation: Explicación técnica del algoritmo ML
    """
    film_id: Optional[int] = Field(
        description="🆔 **ID de Película** - Identificador único (null para fallback a popularidad)",
        examples=[123, 456, None],
        ge=1
    )
    title: str = Field(
        description="🎭 **Título de la Película** - Nombre completo de la película recomendada",
        examples=["The Matrix", "Blade Runner 2049", "Inception", "Interstellar"]
    )
    similarity_score: float = Field(
        description="📊 **Score de Similitud** - Puntuación semántica entre 0.0 (sin similitud) y 1.0 (idéntico)",
        examples=[0.89, 0.76, 0.92, 0.0],
        ge=0.0,
        le=1.0
    )
    explanation: str = Field(
        description="🧠 **Explicación ML** - Descripción técnica del algoritmo y motivo de la recomendación",
        examples=[
            "Recomendación ML: Alta similitud temática y estilística",
            "Recomendación ML: Similitud en conceptos de IA y sci-fi",
            "Recomendación por popularidad debido a pocas películas vistas",
            "Recomendación ML: Temas tecnológicos y narrativa reflexiva"
        ]
    )
