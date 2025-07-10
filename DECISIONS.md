# DECISIONS.md

## Elección de Tecnologías

### Backend principal: NestJS (TypeScript)
- **Motivo:** Permite una arquitectura modular, escalable y mantenible. Su integración con TypeScript proporciona seguridad de tipos y autocompletado avanzado.
- **Alternativas consideradas:** Express, Koa. Se eligió NestJS por su estructura orientada a controladores, servicios y módulos, y su integración nativa con herramientas modernas.

### Microservicio de IA: FastAPI (Python)
- **Motivo:** Permite exponer modelos de machine learning y lógica de recomendación avanzada de forma rápida y eficiente. Python es el estándar para ML y FastAPI ofrece gran rendimiento y documentación automática.
- **Alternativas consideradas:** Flask, Django REST. FastAPI fue preferido por su velocidad y facilidad de integración con librerías de ML.

### ORM: Prisma
- **Motivo:** Prisma ofrece un enfoque schema-first, seguridad de tipos, migraciones robustas y una experiencia de desarrollo moderna. Facilita la integración con NestJS y mejora la productividad.
- **Alternativas consideradas:** TypeORM. Prisma fue elegido por su robustez en migraciones, autocompletado y menor propensión a errores en proyectos nuevos.

### Base de datos: PostgreSQL
- **Motivo:** Soporta consultas avanzadas, búsqueda full-text y es ampliamente adoptado en la industria. Permite escalar y soporta operaciones complejas requeridas por los algoritmos de recomendación.

### Cache: Redis
- **Motivo:** Mejora el rendimiento de la API cacheando resultados de consultas costosas y respuestas de ML. Es rápido, fácil de integrar y ampliamente soportado.

### Contenedores: Docker y docker-compose
- **Motivo:** Facilitan el despliegue, la replicabilidad y la gestión de entornos de desarrollo y producción.

---

## Model Design y Trade-offs

### Arquitectura de Microservicios
- **Ventaja:** Permite desacoplar la lógica de negocio (NestJS) de la lógica de IA (FastAPI), facilitando la escalabilidad y el mantenimiento independiente de cada componente.
- **Trade-off:** Mayor complejidad en la orquestación y comunicación entre servicios, pero se compensa con la flexibilidad y escalabilidad.

### Diseño del Motor de Recomendaciones
- **Recomendaciones v2:**
  - Se utiliza un sistema de puntuación ponderada basado en coincidencias de categorías, actores, idioma y rating, ajustable dinámicamente con el parámetro `focus`.
  - **Ventaja:** Permite recomendaciones personalizadas y explicables.
  - **Trade-off:** Consultas SQL complejas, pero optimizadas con CTEs y agregaciones.
- **Exclusión de películas ya vistas:**
  - Se asegura que las recomendaciones sean siempre relevantes y nuevas para el usuario.
- **Campo `explanation`:**
  - Cada recomendación incluye una justificación, mejorando la transparencia y experiencia de usuario.

### Machine Learning y Fulltext
- **ML (TF-IDF + Coseno):**
  - Permite recomendaciones semánticas y personalizadas, con fallback a popularidad para usuarios nuevos.
  - **Trade-off:** Requiere procesamiento adicional y cache para eficiencia.
- **Fulltext (PostgreSQL):**
  - Permite recomendaciones temáticas y semánticas usando capacidades nativas de la base de datos.

### Prisma y Serialización de BigInt
- **Problema:** PostgreSQL puede devolver valores BigInt que no son serializables por JSON.
- **Solución:** Se añadió un polyfill para convertir BigInt a Number antes de la serialización, asegurando compatibilidad y robustez.

### Organización de Endpoints
- **Decisión:** Consolidar todos los endpoints de recomendación bajo un único controlador para mejorar la mantenibilidad y claridad del código.

---

## Resumen

Las decisiones tecnológicas y de diseño tomadas buscan maximizar la calidad, mantenibilidad y escalabilidad del sistema, priorizando la experiencia de desarrollo, la robustez y la transparencia para el usuario final. Cada elección está justificada por la necesidad de un sistema moderno, seguro y fácil de evolucionar.
