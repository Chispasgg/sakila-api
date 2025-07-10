# 🎬 Sakila AI Recommendation Engine API - byPGG

<p align="center">
  <img src="https://img.shields.io/badge/NestJS-E0234E?style=for-the-badge&logo=nestjs&logoColor=white" alt="NestJS">
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Prisma-2D3748?style=for-the-badge&logo=prisma&logoColor=white" alt="Prisma">
</p>

<p align="center">
  <strong>🚀 Motor de recomendaciones de películas con IA construido sobre la base de datos Sakila</strong>
</p>

<p align="center">
  <a href="#arquitectura-visual">🖼️ Arquitectura Visual</a> •
  <a href="#descripci%C3%B3n-general-del-proyecto">🏃 Descripción</a> •
  <a href="#arquitectura">🏗️ Arquitectura</a> •
  <a href="#pasos-para-el-despliegue-y-funcionamiento">🚀 Despliegue</a> •
  <a href="#acceso-a-servicios">🌐 Acceso a servicios</a> •
  <a href="#decisiones-de-arquitectura-y-dise%C3%B1o">🧠 Decisiones</a>
</p>



## Descripción General del Proyecto

Este repositorio contiene una solución completa para un sistema de recomendaciones de películas basado en la base de datos Sakila. El sistema está compuesto por dos proyectos principales:

---

### 1. `motor_ia` (Python, FastAPI)

Microservicio de inteligencia artificial que implementa diferentes algoritmos de recomendación:

- **Por categorías/actores:** Basado en preferencias de géneros y reparto.
- **Fulltext:** Búsqueda semántica usando PostgreSQL Full-Text Search.
- **Machine Learning:** Recomendaciones personalizadas usando TF-IDF y similitud coseno.

### 2. `sakila-ai-api` (TypeScript, NestJS)

API principal que orquesta la lógica de negocio, expone endpoints REST y consume el microservicio de IA para recomendaciones avanzadas. Utiliza PostgreSQL (Prisma ORM) y Redis para cache.

## Arquitectura

- **Microservicios:** Separación clara entre lógica de negocio (NestJS) y lógica de IA (FastAPI).
- **Base de datos:** PostgreSQL con el esquema Sakila extendido.
- **Cache:** Redis para mejorar el rendimiento.
- **Contenedores:** Uso de Docker y docker-compose para facilitar el despliegue y la gestión de servicios.

### Arquitectura Visual

<p align="center">
  <img src="./arquitectura.png" alt="Arquitectura Sakila AI" width="600"/>
</p>

## Pasos para el Despliegue y Funcionamiento

### 1. Requisitos previos

- Docker y docker-compose instalados
- Python 3.8+ y pip
- Node.js (recomendado usar NVM)

### 2. Despliegue automático (recomendado)

Ejecuta el script principal desde la raíz del proyecto:

```bash
./run.sh
```

Este script:

- Detiene cualquier contenedor Docker previo.
- Llama al lanzador de la API (`lanzar_run.sh`), que:
  - Pregunta si deseas limpiar y configurar el entorno desde cero.
  - Levanta los servicios Docker (PostgreSQL y Redis).
  - Instala dependencias Python y Node.js.
  - Genera la base de datos Sakila y sincroniza Prisma.
  - Espera a que los servicios estén "healthy" y deja el sistema listo para usar.

### 3. Acceso y pruebas

- La API principal estará disponible en: `http://localhost:3000/api` (Swagger UI)
- El microservicio de IA (FastAPI) suele correr en el puerto `2207`.
- Puedes probar los endpoints de recomendaciones, salud y machine learning desde Swagger o con herramientas como `curl` o Postman.

### 4. Notas adicionales

- El sistema soporta reinicio y limpieza automática de datos si así lo deseas.
- Toda la configuración de entorno se puede ajustar en los archivos `.env` y `.env.example`.
- Consulta los archivos `README.md` y documentación interna para detalles avanzados de cada módulo.

### 5. Acceso a servicios
- API Principal: http://localhost:3000
- Motor IA: http://localhost:2207
- Documentación Swagger: http://localhost:3000/api, http://localhost:2207/docs

---

## Decisiones de Arquitectura y Diseño

Para conocer en detalle las decisiones tecnológicas, de diseño de modelo y los trade-offs realizados en este proyecto, consulta el archivo [DECISIONS.md](./DECISIONS.md).

---

Para dudas técnicas, revisa la documentación o contacta al equipo de desarrollo.
