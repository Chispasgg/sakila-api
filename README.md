# 🎬 Sakila AI Project - Resumen Ejecutivo

Sakila AI Project es una plataforma de recomendaciones de películas basada en inteligencia artificial, diseñada con microservicios y tecnologías modernas para ofrecer personalización, escalabilidad y facilidad de despliegue.

## Arquitectura Visual

<p align="center">
  <img src="./arquitectura.png" alt="Arquitectura Sakila AI" width="600"/>
</p>

## ¿Qué resuelve?
- Recomendaciones personalizadas de películas para usuarios finales
- Dashboards y métricas para empresas
- Ejemplo de arquitectura moderna para desarrolladores

## Componentes Clave
- **API Principal (NestJS + TypeScript):** Gestión de usuarios, películas, feedback y dashboards
- **Motor de IA (FastAPI + Python):** 4 algoritmos de recomendación (colaborativo, contenido, sentimientos, full-text)
- **Base de Datos (PostgreSQL + Redis):** Esquema extendido y cache distribuido
- **Infraestructura Docker:** Despliegue rápido y portable

## Principales Decisiones
- Microservicios para escalabilidad y mantenibilidad
- Prisma ORM por seguridad de tipos y productividad
- Redis para acelerar respuestas
- Testing exhaustivo y documentación integrada

## ¿Cómo se usa?
1. Clona el repositorio y configura las variables de entorno
2. Prepara la base de datos con los scripts incluidos
3. Levanta los servicios con Docker Compose
4. Accede a la API y a la documentación Swagger

## Casos de Uso
- Usuarios: recomendaciones y feedback
- Empresas: análisis de comportamiento
- Devs: referencia de arquitectura y ML

## Documentación
- Documentación extendida y guías en las carpetas `sakila-ai-api/documentacion/` y `motor_ia/documentacion/`
- [Ver documentación extendida del proyecto (README_EXTENDIDO.md)](./README_EXTENDIDO.md)

---
<p align="center">
  <strong>🎬 Sakila AI Project - Tecnología moderna para recomendaciones inteligentes</strong>
</p>


