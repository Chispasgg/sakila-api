# 🎬 Sakila AI Project - Sistema Completo de Recomendaciones

<p align="center">
  <img src="https://img.shields.io/badge/NestJS-E0234E?style=for-the-badge&logo=nestjs&logoColor=white" alt="NestJS">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Prisma-2D3748?style=for-the-badge&logo=prisma&logoColor=white" alt="Prisma">
</p>

<p align="center">
  <strong>🚀 Ecosistema completo de recomendaciones de películas con IA distribuido en microservicios</strong>
</p>

---

## 📖 Descripción del Proyecto

**Sakila AI Project** es una solución empresarial completa que combina dos componentes principales para crear un potente sistema de recomendaciones de películas basado en inteligencia artificial. El proyecto utiliza la famosa base de datos **Sakila** como foundation y construye sobre ella un ecosistema moderno y escalable.

### 🏗️ Arquitectura del Sistema

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

---

## 🎯 Componentes del Proyecto

### 🟦 **API Principal - NestJS** (`sakila-ai-api/`)
- **Framework**: NestJS con TypeScript
- **Base de datos**: PostgreSQL con Prisma ORM
- **Cache**: Redis para optimización de consultas
- **Funcionalidades**:
  - ✅ Gestión completa de clientes y películas
  - ✅ Sistema de feedback y puntuaciones
  - ✅ Integración con motor de IA para recomendaciones
  - ✅ API REST documentada con Swagger
  - ✅ Sistema de autenticación y autorización
  - ✅ Optimizaciones de performance con cache

### 🐍 **Motor de IA - Python** (`motor_ia/`)
- **Framework**: FastAPI con Python
- **Algoritmos**: Machine Learning y análisis de datos
- **Funcionalidades**:
  - 🤖 **4 tipos de recomendaciones**:
    - Filtrado colaborativo
    - Recomendaciones basadas en contenido
    - Análisis de sentimientos de reseñas
    - Búsqueda full-text inteligente
  - 📊 Procesamiento de datos en tiempo real
  - 🎯 Recomendaciones personalizadas
  - 📈 Métricas y análisis de rendimiento

### 🗄️ **Infraestructura de Datos** (`datos_docker/`)
- **PostgreSQL**: Base de datos principal con esquema Sakila extendido
- **Redis**: Sistema de cache distribuido
- **Docker**: Contenedorización completa del stack

---

## 🌟 Características Principales

### 🎬 **Sistema de Recomendaciones Inteligente**
- **Múltiples algoritmos**: Combina diferentes enfoques de IA para máxima precisión
- **Personalización**: Recomendaciones adaptadas al histórico del usuario
- **Tiempo real**: Respuestas optimizadas con cache inteligente
- **Escalabilidad**: Arquitectura preparada para grandes volúmenes de datos

### 🔧 **Tecnologías Modernas**
- **Microservicios**: Separación clara de responsabilidades
- **TypeScript**: Desarrollo type-safe en el frontend API
- **Python**: Potencia de ML y análisis de datos
- **Docker**: Despliegue consistente en cualquier entorno
- **Testing**: Cobertura completa de tests automatizados

### 📊 **Performance y Escalabilidad**
- **Cache distribuido**: Redis para consultas frecuentes
- **Optimización de queries**: Índices y consultas optimizadas
- **Arquitectura modular**: Fácil escalado horizontal
- **Monitoreo**: Logs y métricas integradas

---

## 🚀 Stack Tecnológico

### **Backend API**
- **NestJS** - Framework enterprise Node.js
- **TypeScript** - JavaScript tipado
- **Prisma** - ORM moderno y type-safe
- **PostgreSQL** - Base de datos relacional
- **Redis** - Cache en memoria

### **Motor de IA**
- **FastAPI** - Framework Python para APIs
- **scikit-learn** - Machine Learning
- **pandas/numpy** - Análisis de datos
- **NLTK/spaCy** - Procesamiento de lenguaje natural
- **pytest** - Testing framework

### **Infraestructura**
- **Docker & Docker Compose** - Contenedorización
- **PostgreSQL** - Almacenamiento principal
- **Redis** - Cache y sesiones
- **Nginx** - Proxy reverso (en producción)

---

## 📁 Estructura del Proyecto

```
sakila-ai/
├── 📂 sakila-ai-api/          # API Principal NestJS
│   ├── src/                   # Código fuente de la API
│   ├── test/                  # Tests E2E y unitarios
│   ├── prisma/                # Esquemas y migraciones
│   ├── docker/                # Configuración Docker
│   └── documentacion/         # Documentación técnica
│
├── 📂 motor_ia/               # Motor de IA Python
│   ├── src/                   # Algoritmos y endpoints
│   ├── tests/                 # Tests del motor IA
│   ├── docker/                # Docker para Python
│   └── requirements.txt       # Dependencias Python
│
├── 📂 datos_docker/           # Infraestructura de datos
│   ├── postgres/              # Configuración PostgreSQL
│   └── redis/                 # Configuración Redis
│
└── 📄 README.md               # Este archivo
```

---

## 🎯 Casos de Uso

### 👥 **Para Usuarios Finales**
- Descubrir películas personalizadas basadas en gustos previos
- Explorar catálogo de películas con búsqueda inteligente
- Recibir recomendaciones basadas en análisis de sentimientos
- Sistema de puntuaciones y feedback

### 🏢 **Para Empresas**
- Aumentar engagement de usuarios con recomendaciones precisas
- Optimizar catálogo de contenido basado en preferencias
- Análisis de comportamiento de usuarios
- Sistema escalable para millones de usuarios

### 👨‍💻 **Para Desarrolladores**
- Arquitectura de referencia para sistemas de recomendaciones
- Implementación de múltiples algoritmos de ML
- Ejemplo de microservicios con NestJS y FastAPI
- Buenas prácticas de testing y documentación

---

## 📚 Documentación Técnica

Cada componente del proyecto cuenta con su propia documentación detallada:

- 📖 **[API NestJS](./sakila-ai-api/README.md)** - Documentación completa de la API principal
- 🤖 **[Motor IA](./motor_ia/README_PERKSS.md)** - Documentación del sistema de recomendaciones
- 🐳 **[Docker Setup](./sakila-ai-api/docker/README.md)** - Guías de despliegue
- 📊 **[Base de Datos](./sakila-ai-api/documentacion/database.md)** - Esquemas y relaciones

---

## 🚦 Estado del Proyecto

### ✅ **Completado**
- ✅ API REST completa con NestJS
- ✅ Motor de IA con 4 algoritmos de recomendación
- ✅ Base de datos Sakila extendida
- ✅ Sistema de cache con Redis
- ✅ Tests automatizados (100% passing)
- ✅ Documentación Swagger
- ✅ Contenedorización Docker

### 🔄 **En Desarrollo**
- 🔄 Dashboard de administración
- 🔄 Métricas avanzadas de performance
- 🔄 Sistema de notificaciones
- 🔄 API versioning avanzado

---

## 👥 Equipo y Contribuciones

Este proyecto ha sido desarrollado como una demostración técnica de capacidades en:
- Arquitectura de microservicios
- Sistemas de recomendaciones con IA
- Desarrollo full-stack moderno
- DevOps y containerización

---

## 📄 Licencia

Este proyecto es una demostración técnica. La base de datos Sakila es de uso libre para fines educativos y de demostración.

---

<p align="center">
  <strong>🎬 Sakila AI Project - Donde la tecnología moderna se encuentra con el entretenimiento inteligente</strong>
</p>
