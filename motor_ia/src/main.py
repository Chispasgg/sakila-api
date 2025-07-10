"""
Motor de IA - Perkss API

API FastAPI para sistema de recomendaciones de películas basado en la base de datos Sakila.
Proporciona múltiples algoritmos de recomendación incluyendo:
- Recomendaciones por categorías/actores
- Recomendaciones por análisis de texto completo (fulltext)
- Recomendaciones por machine learning (TF-IDF + similitud coseno)

Arquitectura:
- FastAPI como framework web
- PostgreSQL con esquema Sakila como base de datos
- scikit-learn para algoritmos de ML
- Inyección de dependencias para servicios de BD

Versión: 0.1.0
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.endpoints.status import status
from src.endpoints.recommendations import recommendations
from src.endpoints.fulltext_recommendations import router as fulltext_recommendations_router
from src.endpoints.ml_recommendations import router as ml_recommendations_router
from src.dependencies import get_db_service

# Configuración de la aplicación FastAPI
app = FastAPI(
    title="🤖 Motor de IA - Perkss",
    description="""
# 🎬 API de Recomendaciones de Películas

> **Sistema inteligente de recomendaciones** basado en la base de datos **Sakila** con múltiples algoritmos de IA.

## 🚀 Características Principales

| Algoritmo | Descripción | Tecnología |
|-----------|-------------|------------|
| **📂 Categorías/Actores** | Recomendaciones basadas en géneros y reparto | Análisis de preferencias |
| **📝 Análisis de Texto** | Búsqueda semántica en descripciones | PostgreSQL Full-text Search |
| **🧠 Machine Learning** | Similitud vectorial avanzada | TF-IDF + Similitud Coseno |

## 📊 Tecnologías

- **🐘 Base de Datos**: PostgreSQL con esquema Sakila
- **⚡ Framework**: FastAPI con documentación automática
- **🤖 IA/ML**: scikit-learn para algoritmos de recomendación
- **🔧 Arquitectura**: Microservicios con inyección de dependencias

## 🛠️ Endpoints Disponibles

### 🏥 Health Check
- **`GET /status`** - Verificación del estado del servicio

### 🎯 Recomendaciones
- **`GET /recommendations`** - Recomendaciones por categorías/actores
- **`GET /fulltext-recommendations`** - Análisis de texto completo
- **`GET /ml/recommendations/{customer_id}`** - Machine Learning avanzado

## 📈 Casos de Uso

1. **🎭 Recomendaciones por Género**: Ideal para usuarios con preferencias claras
2. **📖 Búsqueda Semántica**: Para encontrar películas con tramas similares
3. **🔮 IA Personalizada**: Algoritmos que aprenden de patrones complejos

---

### 💡 **Tip**: Comienza con `/status` para verificar que el servicio está funcionando correctamente.

### 🔗 **Documentación**: Todos los endpoints incluyen ejemplos interactivos en esta interfaz.
    """,
    version="1.0.0",
    contact={
        "name": "🏢 Perkss Development Team",
        "email": "dev@perkss.com",
        "url": "https://perkss.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    terms_of_service="https://perkss.com/terms",
    servers=[
        {
            "url": "http://localhost:2207",
            "description": "🛠️ Servidor de Desarrollo"
        },
        {
            "url": "https://api.perkss.com",
            "description": "🚀 Servidor de Producción"
        }
    ]
)

# Configuración de CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers con tags organizados y emojis
app.include_router(status.router, tags=["🏥 Health Check"])
app.include_router(recommendations.router, tags=["🎬 Recomendaciones"])
app.include_router(fulltext_recommendations_router, tags=["🔍 Análisis Textual"])
app.include_router(ml_recommendations_router, tags=["🤖 Machine Learning"])
