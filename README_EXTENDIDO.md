# 🎬 Sakila AI Project - Documentación Extendida

## Índice
- [Introducción](#introducción)
- [Motivación y Decisiones de Diseño](#motivación-y-decisiones-de-diseño)
- [Arquitectura General](#arquitectura-general)
- [Componentes y Detalles Técnicos](#componentes-y-detalles-técnicos)
- [Instalación y Puesta en Marcha](#instalación-y-puesta-en-marcha)
- [Flujo de Recomendaciones y Algoritmos](#flujo-de-recomendaciones-y-algoritmos)
- [Base de Datos y Scripts SQL](#base-de-datos-y-scripts-sql)
- [Testing y Calidad](#testing-y-calidad)
- [Despliegue con Docker](#despliegue-con-docker)
- [Casos de Uso](#casos-de-uso)
- [Referencias y Documentación](#referencias-y-documentación)

---

## Introducción

Sakila AI Project es una solución empresarial de recomendaciones de películas basada en IA, construida sobre la base de datos Sakila y desplegada como microservicios. El objetivo es ofrecer recomendaciones personalizadas, dashboards de usuario y un sistema robusto, escalable y documentado.

## Motivación y Decisiones de Diseño

- **Microservicios**: Separación clara entre API (NestJS) y motor de IA (FastAPI) para escalabilidad y mantenibilidad.
- **Prisma ORM**: Elegido por su seguridad de tipos y experiencia de desarrollo superior.
- **Redis**: Cache distribuido para acelerar respuestas y reducir carga en la base de datos.
- **Docker**: Facilita el despliegue y la portabilidad entre entornos.
- **Testing exhaustivo**: Cobertura total para garantizar calidad y robustez.

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    SAKILA AI PROJECT                        │
├─────────────────────────────────────────────────────────────┤
│  🎯 API Principal (NestJS)     │  🤖 Motor de IA (Python)   │
│  ├─ Gestión de usuarios        │  ├─ Algoritmos ML           │
│  ├─ CRUD de películas          │  ├─ Análisis de sentimientos │
│  ├─ Sistema de feedback        │  ├─ Búsqueda por texto      │
│  ├─ Cache con Redis            │  ├─ Recomendaciones híbridas │
│  └─ Documentación Swagger      │  └─ API REST FastAPI        │
├─────────────────────────────────────────────────────────────┤
│              📊 Base de Datos PostgreSQL + Redis            │
│               🐳 Infraestructura Docker                     │
└─────────────────────────────────────────────────────────────┘
```

## Componentes y Detalles Técnicos

### API Principal (NestJS)
- Framework: NestJS + TypeScript
- ORM: Prisma
- Funcionalidades: CRUD, feedback, integración IA, autenticación, cache, documentación Swagger
- Dashboards de usuario y métricas

### Motor de IA (FastAPI)
- Framework: FastAPI + Python
- Algoritmos: Filtrado colaborativo, contenido, análisis de sentimientos, full-text
- ML: scikit-learn, pandas, numpy, NLTK/spaCy
- Testing: pytest

### Infraestructura de Datos
- PostgreSQL: Esquema Sakila extendido
- Redis: Cache distribuido
- Scripts SQL y automatización con Python

## Instalación y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone <repo_url>
cd sakila-ai
```

### 2. Configurar variables de entorno
- Copiar y editar `.env.example` en cada servicio

### 3. Preparar la base de datos
- Usar los scripts de `sql_files/` o el script Python `generar_sakila_db.py` para crear y poblar la BD

### 4. Levantar los servicios con Docker
```bash
cd docker
docker-compose up --build
```

### 5. Acceso a servicios
- API Principal: http://localhost:3000
- Motor IA: http://localhost:2207
- Documentación Swagger: http://localhost:3000/api, http://localhost:2207/docs

## Flujo de Recomendaciones y Algoritmos

- **V1**: Basado en reglas (categorías, actores, idioma, rating)
- **V2**: Algoritmo avanzado con pesos dinámicos
- **ML Externo**: Similitud semántica vía FastAPI
- **Full-Text**: PostgreSQL GIN y análisis semántico
- **Feedback**: Los usuarios valoran recomendaciones, mejorando el sistema

## Base de Datos y Scripts SQL
- Esquema y datos en `sql_files/`
- Script Python automatiza la creación y carga
- Índices optimizados para búsquedas y recomendaciones

## Testing y Calidad
- Tests unitarios y E2E en ambos servicios
- 100% de tests pasando
- Cobertura de endpoints y lógica de negocio

## Despliegue con Docker
- Dockerfiles y docker-compose para cada microservicio
- Soporte para entornos de desarrollo y producción
- Comandos útiles para logs, backup y restauración

## Casos de Uso
- Usuarios: recomendaciones personalizadas, feedback, exploración
- Empresas: análisis de comportamiento, optimización de catálogo
- Desarrolladores: referencia de arquitectura, integración ML, buenas prácticas

## Referencias y Documentación
- Documentación extendida en `sakila-ai-api/documentacion/` y `motor_ia/documentacion/`
- Guías de despliegue, decisiones técnicas y detalles de base de datos

---

<p align="center">
  <strong>🎬 Sakila AI Project - Donde la tecnología moderna se encuentra con el entretenimiento inteligente</strong>
</p>
