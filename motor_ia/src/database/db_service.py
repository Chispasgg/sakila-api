"""
Servicio de base de datos para el sistema de recomendaciones de películas.

Proporciona acceso a datos de la base de datos PostgreSQL con esquema Sakila
y implementa algoritmos de recomendación basados en:
- Categorías y géneros de películas
- Actores y reparto
- Análisis de texto completo (fulltext search)
- Machine Learning con TF-IDF y similitud coseno

El servicio maneja conexiones de BD, cache de modelos ML y optimizaciones
de consultas para el sistema de recomendaciones.
"""

import psycopg2
from psycopg2 import Error, pool
from typing import List, Dict, Any, Optional
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Servicio principal para operaciones de base de datos y recomendaciones.
    
    Implementa patrones singleton para cache de modelos ML y manejo eficiente
    de conexiones para mejorar performance en el sistema de recomendaciones.
    
    Attributes:
        _tfidf_vectorizer: Vectorizador TF-IDF cacheado (singleton)
        _tfidf_matrix: Matriz TF-IDF de todas las películas (singleton)
        _all_films_data: Cache de datos de todas las películas (singleton)
        _connection_pool: Pool de conexiones a base de datos
    """
    
    # Variables de clase para cache singleton
    _tfidf_vectorizer: Optional[TfidfVectorizer] = None
    _tfidf_matrix: Optional[Any] = None  # Sparse matrix type
    _all_films_data: Optional[List[Dict[str, Any]]] = None
    _connection_pool: Optional[pool.SimpleConnectionPool] = None

    def __init__(self, database_url: str):
        """
        Inicializa el servicio de base de datos.
        
        Args:
            database_url: URL de conexión a PostgreSQL
        """
        self.database_url = database_url
        self._init_connection_pool()

    def _init_connection_pool(self) -> None:
        """
        Inicializa el pool de conexiones para mejor performance.
        
        Optimización: Utiliza pool de conexiones para evitar overhead
        de establecer/cerrar conexiones constantemente.
        """
        try:
            if DatabaseService._connection_pool is None:
                DatabaseService._connection_pool = pool.SimpleConnectionPool(
                    1, 20,  # min y max conexiones
                    self.database_url
                )
                logger.info("Pool de conexiones inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando pool de conexiones: {e}")
            DatabaseService._connection_pool = None

    def _get_connection(self):
        """
        Obtiene una conexión del pool o crea una nueva.
        
        Returns:
            Conexión a la base de datos
        """
        try:
            if DatabaseService._connection_pool:
                return DatabaseService._connection_pool.getconn()
            else:
                # Fallback a conexión directa si el pool falla
                return psycopg2.connect(self.database_url)
        except Error as e:
            logger.error(f"Error al obtener conexión: {e}")
            return None

    def _return_connection(self, conn) -> None:
        """
        Retorna una conexión al pool.
        
        Args:
            conn: Conexión a retornar
        """
        try:
            if DatabaseService._connection_pool and conn:
                DatabaseService._connection_pool.putconn(conn)
            elif conn:
                conn.close()
        except Exception as e:
            logger.error(f"Error retornando conexión al pool: {e}")

    def _connect(self):
        """
        Método legacy para compatibilidad con código existente.
        
        Returns:
            Conexión a la base de datos
            
        Note:
            Método mantenido para compatibilidad hacia atrás.
            Se recomienda usar _get_connection() para nuevos desarrollos.
        """
        return self._get_connection()

    def _execute_query_with_connection_handling(self, query: str, params: tuple = ()) -> List[tuple]:
        """
        Ejecuta una consulta SQL con manejo automático de conexiones.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Lista de tuplas con los resultados
            
        Optimización: Centraliza el manejo de conexiones y errores.
        """
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute(query, params)
                results = cur.fetchall()
                cur.close()
                return results
            return []
        except Error as e:
            logger.error(f"Error ejecutando consulta: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_all_tables(self) -> List[str]:
        """
        Obtiene lista de todas las tablas en el esquema public.
        
        Returns:
            Lista de nombres de tablas
        """
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        results = self._execute_query_with_connection_handling(query)
        return [row[0] for row in results]

    def get_all_films_data(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los datos necesarios de las películas para el motor de recomendación ML.
        Incluye film_id, title, description, category, actors, language, rating, fulltext.
        """
        if DatabaseService._all_films_data is not None:
            return DatabaseService._all_films_data

        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT
                        f.film_id,
                        f.title,
                        f.description,
                        c.name AS category_name,
                        ARRAY_AGG(DISTINCT a.first_name || ' ' || a.last_name) AS actors,
                        l.name AS language_name,
                        f.rating,
                        f.fulltext
                    FROM film f
                    LEFT JOIN film_category fc ON f.film_id = fc.film_id
                    LEFT JOIN category c ON fc.category_id = c.category_id
                    LEFT JOIN language l ON f.language_id = l.language_id
                    LEFT JOIN film_actor fa ON f.film_id = fa.film_id
                    LEFT JOIN actor a ON fa.actor_id = a.actor_id
                    GROUP BY f.film_id, f.title, f.description, c.name, l.name, f.rating, f.fulltext
                    ORDER BY f.film_id;
                """
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                films_data = []
                for row in cur.fetchall():
                    film_dict = dict(zip(columns, row))
                    # Ensure actors is a list, even if NULL from ARRAY_AGG
                    if film_dict['actors'] is None:
                        film_dict['actors'] = []
                    films_data.append(film_dict)
                cur.close()
                DatabaseService._all_films_data = films_data
                return films_data
            return []
        except Error as e:
            print(f"Error al obtener todos los datos de las películas: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def _generate_film_vector_text(self, film_data: Dict[str, Any]) -> str:
        """Genera una cadena de texto combinada para el vector de una película."""
        actors_list = film_data.get('actors', [])
        # Filtrar cualquier valor None que pueda venir de la base de datos
        actors_str = ' '.join([actor for actor in actors_list if actor is not None])

        parts = [
            film_data.get('title', ''),
            film_data.get('description', ''),
            film_data.get('category_name', ''),
            actors_str,
            film_data.get('language_name', ''),
            str(film_data.get('rating', '')),  # Asegurar que el rating sea string
            film_data.get('fulltext', '')
        ]
        return ' '.join(filter(None, parts)).lower()

    def _build_tfidf_model(self):
        """Construye y cachea el modelo TF-IDF y la matriz de todas las películas."""
        if DatabaseService._tfidf_vectorizer is None or DatabaseService._tfidf_matrix is None:
            all_films_data = self.get_all_films_data()
            if not all_films_data:
                print("No hay datos de películas para construir el modelo TF-IDF.")
                return

            corpus = [self._generate_film_vector_text(film) for film in all_films_data]
            
            vectorizer = TfidfVectorizer(stop_words='english' if 'english' in corpus[0] else None) # Simple stop words for English
            tfidf_matrix = vectorizer.fit_transform(corpus)

            DatabaseService._tfidf_vectorizer = vectorizer
            DatabaseService._tfidf_matrix = tfidf_matrix
            print("Modelo TF-IDF construido y cacheado.")
        else:
            print("Modelo TF-IDF ya cacheado.")

    def get_watched_movies_by_customer(self, customer_id: int) -> List[str]:
        """Obtiene una lista de películas vistas por un cliente dado su ID."""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT DISTINCT f.title
                    FROM film f
                    JOIN inventory i ON f.film_id = i.film_id
                    JOIN rental r ON i.inventory_id = r.inventory_id
                    WHERE r.customer_id = %s
                    ORDER BY f.title;
                """
                cur.execute(query, (customer_id,))
                movies = [row[0] for row in cur.fetchall()]
                cur.close()
                return movies
            return []
        except Error as e:
            print(f"Error al obtener películas vistas por el cliente {customer_id}: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_film_details_for_customer(self, customer_id: int) -> List[dict]:
        """
        Recupera detalles de las películas vistas por un cliente, incluyendo duración, coste,
        texto completo y actores.
        """
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT
                        f.title,
                        f.rental_duration,
                        f.rental_rate,
                        f.fulltext,
                        ARRAY_AGG(a.first_name || ' ' || a.last_name ORDER BY a.first_name, a.last_name) AS actors
                    FROM film f
                    JOIN inventory i ON f.film_id = i.film_id
                    JOIN rental r ON i.inventory_id = r.inventory_id
                    LEFT JOIN film_actor fa ON f.film_id = fa.film_id
                    LEFT JOIN actor a ON fa.actor_id = a.actor_id
                    WHERE r.customer_id = %s
                    GROUP BY f.film_id, f.title, f.rental_duration, f.rental_rate, f.fulltext
                    ORDER BY f.title;
                """
                cur.execute(query, (customer_id,))
                results = []
                for row in cur.fetchall():
                    results.append({
                        "title": row[0],
                        "rental_duration": row[1],
                        "rental_rate": float(row[2]),
                        "fulltext": row[3],
                        "actors": row[4] if row[4] else []
                    })
                cur.close()
                return results
            return []
        except Error as e:
            print(f"Error al obtener detalles de películas vistas para el cliente {customer_id}: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_watched_films_for_ml(self, customer_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene los film_id y datos relevantes para ML de las películas vistas por un cliente.
        """
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT DISTINCT
                        f.film_id,
                        f.title,
                        f.description,
                        c.name AS category_name,
                        ARRAY_AGG(DISTINCT a.first_name || ' ' || a.last_name) AS actors,
                        l.name AS language_name,
                        f.rating,
                        f.fulltext
                    FROM film f
                    JOIN inventory i ON f.film_id = i.film_id
                    JOIN rental r ON i.inventory_id = r.inventory_id
                    LEFT JOIN film_category fc ON f.film_id = fc.film_id
                    LEFT JOIN category c ON fc.category_id = c.category_id
                    LEFT JOIN language l ON f.language_id = l.language_id
                    LEFT JOIN film_actor fa ON f.film_id = fa.film_id
                    LEFT JOIN actor a ON fa.actor_id = a.actor_id
                    WHERE r.customer_id = %s
                    GROUP BY f.film_id, f.title, f.description, c.name, l.name, f.rating, f.fulltext
                    ORDER BY f.film_id;
                """
                cur.execute(query, (customer_id,))
                columns = [desc[0] for desc in cur.description]
                watched_films_data = []
                for row in cur.fetchall():
                    film_dict = dict(zip(columns, row))
                    if film_dict['actors'] is None:
                        film_dict['actors'] = []
                    watched_films_data.append(film_dict)
                cur.close()
                return watched_films_data
            return []
        except Error as e:
            print(f"Error al obtener películas vistas para ML para el cliente {customer_id}: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_ml_recommendations(self, customer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene recomendaciones de películas basadas en similitud semántica (TF-IDF y Coseno)
        para un cliente dado.
        """
        self._build_tfidf_model() # Asegura que el modelo TF-IDF esté construido y cacheado

        if DatabaseService._tfidf_vectorizer is None or DatabaseService._tfidf_matrix is None:
            print("Error: Modelo TF-IDF no disponible.")
            return []

        watched_films_data = self.get_watched_films_for_ml(customer_id)
        
        # Fallback a popularidad si no hay suficientes películas vistas
        if len(watched_films_data) < 3: # Umbral configurable
            print(f"Pocas películas vistas por el cliente {customer_id}. Recurriendo a recomendaciones por popularidad.")
            popular_titles = self.get_most_popular_movies(
                exclude_film_titles=[f['title'] for f in watched_films_data],
                limit=limit
            )
            # Convertir a formato de salida requerido
            return [{
                "film_id": None, # No disponible en get_most_popular_movies
                "title": title,
                "similarity_score": 0.0, # No aplica similitud
                "explanation": "Recomendación por popularidad debido a pocas películas vistas."
            } for title in popular_titles]

        # 1. Construir el perfil vectorial medio del usuario
        watched_film_texts = [self._generate_film_vector_text(film) for film in watched_films_data]
        watched_film_vectors = DatabaseService._tfidf_vectorizer.transform(watched_film_texts)
        # Convertir el perfil de np.matrix a np.ndarray para compatibilidad con scikit-learn
        user_profile_vector = np.asarray(np.mean(watched_film_vectors, axis=0))

        all_films_data = self.get_all_films_data()
        film_ids = [film['film_id'] for film in all_films_data]
        film_titles = [film['title'] for film in all_films_data]
        
        # 2. Calcular similitud coseno con todas las películas disponibles
        # Reshape user_profile_vector for cosine_similarity
        similarities = cosine_similarity(user_profile_vector, DatabaseService._tfidf_matrix).flatten()

        # 3. Crear una lista de (film_id, title, similarity_score)
        film_scores = []
        for i, film_id in enumerate(film_ids):
            film_scores.append({
                "film_id": film_id,
                "title": film_titles[i],
                "similarity_score": similarities[i]
            })

        # 4. Excluir las películas ya alquiladas
        watched_film_ids = {film['film_id'] for film in watched_films_data}
        filtered_film_scores = [
            fs for fs in film_scores if fs['film_id'] not in watched_film_ids
        ]

        # 5. Devolver las 10 más similares
        recommended_films = sorted(filtered_film_scores, key=lambda x: x['similarity_score'], reverse=True)[:limit]

        # Añadir explicación
        for film in recommended_films:
            film['explanation'] = "Recomendado por similitud semántica con tus películas vistas."
        
        return recommended_films

    def get_genres_from_watched_movies(self, customer_id: int) -> List[str]:
        """Obtiene los géneros de las películas vistas por un cliente."""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT DISTINCT c.name
                    FROM rental r
                    JOIN inventory i ON r.inventory_id = i.inventory_id
                    JOIN film f ON i.film_id = f.film_id
                    JOIN film_category fc ON f.film_id = fc.film_id
                    JOIN category c ON fc.category_id = c.category_id
                    WHERE r.customer_id = %s;
                """
                cur.execute(query, (customer_id,))
                genres = [row[0] for row in cur.fetchall()]
                cur.close()
                return genres
            return []
        except Error as e:
            print(f"Error al obtener géneros de películas vistas para el cliente {customer_id}: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_languages_from_watched_movies(self, customer_id: int) -> List[str]:
        """Obtiene los idiomas de las películas vistas por un cliente."""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT DISTINCT l.name
                    FROM rental r
                    JOIN inventory i ON r.inventory_id = i.inventory_id
                    JOIN film f ON i.film_id = f.film_id
                    JOIN language l ON f.language_id = l.language_id
                    WHERE r.customer_id = %s;
                """
                cur.execute(query, (customer_id,))
                languages = [row[0] for row in cur.fetchall()]
                cur.close()
                return languages
            return []
        except Error as e:
            print(f"Error al obtener idiomas de películas vistas para el cliente {customer_id}: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_popular_movies_by_genres(self, genres: List[str], exclude_film_titles: List[str], limit: int = 10) -> List[str]:
        """Obtiene películas populares dentro de los géneros dados, excluyendo títulos específicos."""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT f.title, COUNT(r.rental_id) AS rental_count
                    FROM film f
                    JOIN inventory i ON f.film_id = i.film_id
                    JOIN rental r ON i.inventory_id = r.rental_id
                    JOIN film_category fc ON f.film_id = fc.film_id
                    JOIN category c ON fc.category_id = c.category_id
                    WHERE c.name IN %s
                """
                params = [tuple(genres)]

                if exclude_film_titles:
                    query += " AND f.title NOT IN %s"
                    params.append(tuple(exclude_film_titles))

                query += """
                    GROUP BY f.title
                    ORDER BY rental_count DESC
                    LIMIT %s;
                """
                params.append(limit)

                cur.execute(query, tuple(params))
                movies = [row[0] for row in cur.fetchall()]
                cur.close()
                return movies
            return []
        except Error as e:
            print(f"Error al obtener películas populares por género: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_popular_movies_by_languages(self, languages: List[str], exclude_film_titles: List[str], limit: int = 10) -> List[str]:
        """Obtiene películas populares dentro de los idiomas dados, excluyendo títulos específicos."""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT f.title, COUNT(r.rental_id) AS rental_count
                    FROM film f
                    JOIN inventory i ON f.film_id = i.film_id
                    JOIN rental r ON i.inventory_id = r.rental_id
                    JOIN language l ON f.language_id = l.language_id
                    WHERE l.name IN %s
                """
                params = [tuple(languages)]

                if exclude_film_titles:
                    query += " AND f.title NOT IN %s"
                    params.append(tuple(exclude_film_titles))

                query += """
                    GROUP BY f.title
                    ORDER BY rental_count DESC
                    LIMIT %s;
                """
                params.append(limit)

                cur.execute(query, tuple(params))
                movies = [row[0] for row in cur.fetchall()]
                cur.close()
                return movies
            return []
        except Error as e:
            print(f"Error al obtener películas populares por idioma: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_most_popular_movies(self, exclude_film_titles: List[str], limit: int = 10) -> List[str]:
        """Obtiene las películas más populares en general, excluyendo títulos específicos."""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT f.title, COUNT(r.rental_id) AS rental_count
                    FROM film f
                    JOIN inventory i ON f.film_id = i.film_id
                    JOIN rental r ON i.inventory_id = r.rental_id
                """
                params = []

                if exclude_film_titles:
                    query += " WHERE f.title NOT IN %s"
                    params.append(tuple(exclude_film_titles))

                query += """
                    GROUP BY f.title
                    ORDER BY rental_count DESC
                    LIMIT %s;
                """
                params.append(limit)

                cur.execute(query, tuple(params) if params else ())
                movies = [row[0] for row in cur.fetchall()]
                cur.close()
                return movies
            return []
        except Error as e:
            print(f"Error al obtener las películas más populares: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_ratings_from_watched_movies(self, customer_id: int) -> List[str]:
        """Obtiene las clasificaciones (ratings) de las películas vistas por un cliente."""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT DISTINCT f.rating
                    FROM rental r
                    JOIN inventory i ON r.inventory_id = i.inventory_id
                    JOIN film f ON i.film_id = f.film_id
                    WHERE r.customer_id = %s AND f.rating IS NOT NULL;
                """
                cur.execute(query, (customer_id,))
                ratings = [row[0] for row in cur.fetchall()]
                cur.close()
                return ratings
            return []
        except Error as e:
            print(f"Error al obtener ratings de películas vistas para el cliente {customer_id}: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_popular_movies_by_ratings(self, ratings: List[str], exclude_film_titles: List[str], limit: int = 10) -> List[str]:
        """Obtiene películas populares dentro de las clasificaciones dadas, excluyendo títulos específicos."""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT f.title, COUNT(r.rental_id) AS rental_count
                    FROM film f
                    JOIN inventory i ON f.film_id = i.film_id
                    JOIN rental r ON i.inventory_id = r.rental_id
                    WHERE f.rating IN %s
                """
                params = [tuple(ratings)]

                if exclude_film_titles:
                    query += " AND f.title NOT IN %s"
                    params.append(tuple(exclude_film_titles))

                query += """
                    GROUP BY f.title
                    ORDER BY rental_count DESC
                    LIMIT %s;
                """
                params.append(limit)

                cur.execute(query, tuple(params))
                movies = [row[0] for row in cur.fetchall()]
                cur.close()
                return movies
            return []
        except Error as e:
            print(f"Error al obtener películas populares por rating: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_fulltext_data_for_customer(self, customer_id: int) -> List[str]:
        """Obtiene el contenido fulltext de las películas vistas por un cliente."""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT DISTINCT f.fulltext
                    FROM film f
                    JOIN inventory i ON f.film_id = i.film_id
                    JOIN rental r ON i.inventory_id = r.rental_id
                    WHERE r.customer_id = %s AND f.fulltext IS NOT NULL;
                """
                cur.execute(query, (customer_id,))
                fulltext_entries = [row[0] for row in cur.fetchall()]
                cur.close()
                return fulltext_entries
            return []
        except Error as e:
            print(f"Error al obtener datos fulltext para el cliente {customer_id}: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def _parse_fulltext_string(self, fulltext_str: str) -> Dict[str, int]:
        """Parsea una cadena fulltext y suma las valoraciones de las palabras."""
        parsed_data = {}
        # El formato es 'palabra':valor 'palabra':valor,valor
        # Usamos regex para encontrar 'palabra':valor o 'palabra':valor,valor
        matches = re.findall(r"'([a-zA-Z]+)':([\d,]+)", fulltext_str)
        for word, values_str in matches:
            # Sumar todas las valoraciones si hay múltiples
            values = sum(int(v) for v in values_str.split(','))
            parsed_data[word] = parsed_data.get(word, 0) + values
        return parsed_data

    def analyze_fulltext_preferences(self, fulltext_data: List[str]) -> Dict[str, int]:
        """Analiza los datos fulltext para identificar los tipos (palabras) preferidos del usuario."""
        aggregated_preferences = {}
        for entry in fulltext_data:
            parsed_entry = self._parse_fulltext_string(entry)
            for word, score in parsed_entry.items():
                aggregated_preferences[word] = aggregated_preferences.get(word, 0) + score
        
        # Opcional: ordenar por puntuación o filtrar los top N
        # sorted_preferences = sorted(aggregated_preferences.items(), key=lambda item: item[1], reverse=True)
        return aggregated_preferences

    def get_movies_by_fulltext_affinity(self, preferred_types: Dict[str, int], exclude_film_titles: List[str], limit: int = 10) -> List[Dict[str, str]]:
        """
        Obtiene películas recomendadas basadas en la afinidad con los tipos (palabras) preferidos
        del usuario en el campo fulltext, excluyendo títulos específicos.
        Devuelve una lista de diccionarios con 'title' y 'fulltext'.
        """
        if not preferred_types:
            return []

        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                # Construir la cláusula WHERE para buscar palabras en fulltext
                # Usamos tsquery para buscar las palabras en el campo tsvector (fulltext)
                # Convertimos las palabras preferidas en un formato de tsquery
                # Ejemplo: 'word1' | 'word2' | 'word3'
                query_parts = []
                for word in preferred_types.keys():
                    query_parts.append(f"'{word}'")
                tsquery_str = " | ".join(query_parts)

                query = f"""
                    SELECT f.title, f.fulltext, ts_rank(f.fulltext, to_tsquery('english', %s)) AS rank
                    FROM film f
                    WHERE f.fulltext @@ to_tsquery('english', %s)
                """
                params = [tsquery_str, tsquery_str]

                if exclude_film_titles:
                    query += " AND f.title NOT IN %s"
                    params.append(tuple(exclude_film_titles))

                query += """
                    ORDER BY rank DESC, f.title ASC
                    LIMIT %s;
                """
                params.append(limit)

                cur.execute(query, tuple(params))
                movies_data = []
                for row in cur.fetchall():
                    movies_data.append({"title": row[0], "fulltext": row[1]})
                cur.close()
                return movies_data
            return []
        except Error as e:
            print(f"Error al obtener recomendaciones por afinidad de fulltext: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_recommended_movies_by_actor_affinity(self, customer_id: int, exclude_film_titles: List[str], limit: int = 10) -> List[str]:
        """
        Obtiene películas recomendadas basadas en la afinidad con los actores de las películas
        vistas por el cliente, excluyendo títulos específicos.
        """
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                # 1. Obtener los actores de las películas vistas por el cliente
                query_watched_actors = """
                    SELECT DISTINCT a.actor_id, a.first_name, a.last_name
                    FROM rental r
                    JOIN inventory i ON r.inventory_id = i.inventory_id
                    JOIN film_actor fa ON i.film_id = fa.film_id
                    JOIN actor a ON fa.actor_id = a.actor_id
                    WHERE r.customer_id = %s;
                """
                cur.execute(query_watched_actors, (customer_id,))
                watched_actor_ids = [row[0] for row in cur.fetchall()]

                if not watched_actor_ids:
                    return [] # No hay actores en las películas vistas

                # 2. Encontrar películas que contengan a esos actores y que el usuario no haya visto
                query_recommendations = """
                    SELECT
                        f.title,
                        COUNT(DISTINCT fa.actor_id) AS matching_actors_count
                    FROM film f
                    JOIN film_actor fa ON f.film_id = fa.film_id
                    WHERE fa.actor_id IN %s
                """
                params = [tuple(watched_actor_ids)]

                if exclude_film_titles:
                    query_recommendations += " AND f.title NOT IN %s"
                    params.append(tuple(exclude_film_titles))

                query_recommendations += """
                    GROUP BY f.title
                    ORDER BY matching_actors_count DESC, f.title ASC
                    LIMIT %s;
                """
                params.append(limit)

                cur.execute(query_recommendations, tuple(params))
                recommended_movies = [row[0] for row in cur.fetchall()]
                cur.close()
                return recommended_movies
            return []
        except Error as e:
            print(f"Error al obtener recomendaciones por afinidad de actor para el cliente {customer_id}: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

# Ejemplo de uso (opcional, para pruebas)
if __name__ == "__main__":
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/sakila"
    db_service = DatabaseService(DATABASE_URL)
    
    print("\n--- Probando get_all_tables ---")
    tables = db_service.get_all_tables()
    if tables:
        print("Tablas en la base de datos 'sakila' (esquema public):")
        for table in tables:
            print(f"- {table}")
    else:
        print("No se pudieron obtener las tablas.")

    print("\n--- Probando get_watched_movies_by_customer (customer_id=1) ---")
    customer_id_test = 1
    watched_movies = db_service.get_watched_movies_by_customer(customer_id_test)
    if watched_movies:
        print(f"Películas vistas por el cliente {customer_id_test}:")
        for movie in watched_movies:
            print(f"- {movie}")
    else:
        print(f"No se pudieron obtener películas para el cliente {customer_id_test} o no ha visto ninguna.")

    print("\n--- Probando get_film_details_for_customer (customer_id=1) ---")
    film_details = db_service.get_film_details_for_customer(customer_id_test)
    if film_details:
        print(f"Detalles de películas vistas por el cliente {customer_id_test}:")
        for detail in film_details:
            print(f"- {detail['title']} (Duración: {detail['rental_duration']}, Coste: {detail['rental_rate']}, Actores: {', '.join(detail['actors'])})")
    else:
        print(f"No se pudieron obtener detalles de películas para el cliente {customer_id_test}.")

    print("\n--- Probando get_genres_from_watched_movies (customer_id=1) ---")
    genres = db_service.get_genres_from_watched_movies(customer_id_test)
    if genres:
        print(f"Géneros de películas vistas por el cliente {customer_id_test}:")
        for genre in genres:
            print(f"- {genre}")
    else:
        print(f"No se pudieron obtener géneros para el cliente {customer_id_test}.")

    print("\n--- Probando get_popular_movies_by_genres (genres=genres, exclude_film_titles=watched_movies) ---")
    if genres and watched_movies:
        recommended_movies_genre = db_service.get_popular_movies_by_genres(genres, watched_movies)
        if recommended_movies_genre:
            print("Películas recomendadas por género:")
            for movie in recommended_movies_genre:
                print(f"- {movie}")
        else:
            print("No se encontraron películas recomendadas por género.")
    else:
        print("No hay suficientes datos para generar recomendaciones por género.")

    print("\n--- Probando get_recommended_movies_by_actor_affinity (customer_id=1, exclude_film_titles=watched_movies) ---")
    if watched_movies:
        recommended_movies_actor = db_service.get_recommended_movies_by_actor_affinity(customer_id_test, watched_movies)
        if recommended_movies_actor:
            print("Películas recomendadas por afinidad de actor:")
            for movie in recommended_movies_actor:
                print(f"- {movie}")
        else:
            print("No se encontraron películas recomendadas por afinidad de actor.")
    else:
        print("No hay películas vistas para generar recomendaciones por afinidad de actor.")

    print("\n--- Probando get_ml_recommendations (customer_id=1) ---")
    ml_recommendations = db_service.get_ml_recommendations(customer_id_test)
    if ml_recommendations:
        print(f"Recomendaciones ML para el cliente {customer_id_test}:")
        for rec in ml_recommendations:
            print(f"- {rec['title']} (Similitud: {rec['similarity_score']:.3f}, Explicación: {rec['explanation']})")
    else:
        print(f"No se pudieron obtener recomendaciones ML para el cliente {customer_id_test}.")


    print("\n--- Probando get_fulltext_data_for_customer (customer_id=1) ---")
    fulltext_data = db_service.get_fulltext_data_for_customer(customer_id_test)
    if fulltext_data:
        print(f"Datos fulltext para el cliente {customer_id_test}:")
        for entry in fulltext_data:
            print(f"- {entry}")
    else:
        print(f"No se encontraron datos fulltext para el cliente {customer_id_test}.")

    print("\n--- Probando analyze_fulltext_preferences (fulltext_data) ---")
    if fulltext_data:
        preferences = db_service.analyze_fulltext_preferences(fulltext_data)
        print(f"Preferencias de fulltext agregadas: {preferences}")
    else:
        print("No hay datos fulltext para analizar preferencias.")

    print("\n--- Probando get_movies_by_fulltext_affinity (preferences, watched_movies) ---")
    if fulltext_data and watched_movies:
        recommended_movies_fulltext = db_service.get_movies_by_fulltext_affinity(preferences, watched_movies)
        if recommended_movies_fulltext:
            print("Películas recomendadas por afinidad de fulltext:")
            for movie in recommended_movies_fulltext:
                print(f"- {movie}")
        else:
            print("No se encontraron películas recomendadas por afinidad de fulltext.")
    else:
        print("No hay suficientes datos para generar recomendaciones por afinidad de fulltext.")

    def get_popular_movies_by_genres(self, genres: List[str], exclude_film_titles: List[str], limit: int = 10) -> List[str]:
        """Obtiene películas populares dentro de los géneros dados, excluyendo títulos específicos."""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                query = """
                    SELECT f.title, COUNT(r.rental_id) AS rental_count
                    FROM film f
                    JOIN inventory i ON f.film_id = i.film_id
                    JOIN rental r ON i.inventory_id = r.inventory_id
                    JOIN film_category fc ON f.film_id = fc.film_id
                    JOIN category c ON fc.category_id = c.category_id
                    WHERE c.name IN %s
                """
                params = [tuple(genres)]

                if exclude_film_titles:
                    query += " AND f.title NOT IN %s"
                    params.append(tuple(exclude_film_titles))

                query += """
                    GROUP BY f.title
                    ORDER BY rental_count DESC
                    LIMIT %s;
                """
                params.append(limit)

                cur.execute(query, tuple(params))
                movies = [row[0] for row in cur.fetchall()]
                cur.close()
                return movies
            return []
        except Error as e:
            print(f"Error al obtener películas populares por género: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

    def get_recommended_movies_by_actor_affinity(self, customer_id: int, exclude_film_titles: List[str], limit: int = 10) -> List[str]:
        """
        Obtiene películas recomendadas basadas en la afinidad con los actores de las películas
        vistas por el cliente, excluyendo títulos específicos.
        """
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                # 1. Obtener los actores de las películas vistas por el cliente
                query_watched_actors = """
                    SELECT DISTINCT a.actor_id, a.first_name, a.last_name
                    FROM rental r
                    JOIN inventory i ON r.inventory_id = i.inventory_id
                    JOIN film_actor fa ON i.film_id = fa.film_id
                    JOIN actor a ON fa.actor_id = a.actor_id
                    WHERE r.customer_id = %s;
                """
                cur.execute(query_watched_actors, (customer_id,))
                watched_actor_ids = [row[0] for row in cur.fetchall()]

                if not watched_actor_ids:
                    return [] # No hay actores en las películas vistas

                # 2. Encontrar películas que contengan a esos actores y que el usuario no haya visto
                query_recommendations = """
                    SELECT
                        f.title,
                        COUNT(DISTINCT fa.actor_id) AS matching_actors_count
                    FROM film f
                    JOIN film_actor fa ON f.film_id = fa.film_id
                    WHERE fa.actor_id IN %s
                """
                params = [tuple(watched_actor_ids)]

                if exclude_film_titles:
                    query_recommendations += " AND f.title NOT IN %s"
                    params.append(tuple(exclude_film_titles))

                query_recommendations += """
                    GROUP BY f.title
                    ORDER BY matching_actors_count DESC, f.title ASC
                    LIMIT %s;
                """
                params.append(limit)

                cur.execute(query_recommendations, tuple(params))
                recommended_movies = [row[0] for row in cur.fetchall()]
                cur.close()
                return recommended_movies
            return []
        except Error as e:
            print(f"Error al obtener recomendaciones por afinidad de actor para el cliente {customer_id}: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)

# Ejemplo de uso (opcional, para pruebas)
if __name__ == "__main__":
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/sakila"
    db_service = DatabaseService(DATABASE_URL)
    
    print("\n--- Probando get_all_tables ---")
    tables = db_service.get_all_tables()
    if tables:
        print("Tablas en la base de datos 'sakila' (esquema public):")
        for table in tables:
            print(f"- {table}")
    else:
        print("No se pudieron obtener las tablas.")

    print("\n--- Probando get_watched_movies_by_customer (customer_id=1) ---")
    customer_id_test = 1
    watched_movies = db_service.get_watched_movies_by_customer(customer_id_test)
    if watched_movies:
        print(f"Películas vistas por el cliente {customer_id_test}:")
        for movie in watched_movies:
            print(f"- {movie}")
    else:
        print(f"No se pudieron obtener películas para el cliente {customer_id_test} o no ha visto ninguna.")

    print("\n--- Probando get_film_details_for_customer (customer_id=1) ---")
    film_details = db_service.get_film_details_for_customer(customer_id_test)
    if film_details:
        print(f"Detalles de películas vistas por el cliente {customer_id_test}:")
        for detail in film_details:
            print(f"- {detail['title']} (Duración: {detail['rental_duration']}, Coste: {detail['rental_rate']}, Actores: {', '.join(detail['actors'])})")
    else:
        print(f"No se pudieron obtener detalles de películas para el cliente {customer_id_test}.")

    print("\n--- Probando get_genres_from_watched_movies (customer_id=1) ---")
    genres = db_service.get_genres_from_watched_movies(customer_id_test)
    if genres:
        print(f"Géneros de películas vistas por el cliente {customer_id_test}:")
        for genre in genres:
            print(f"- {genre}")
    else:
        print(f"No se pudieron obtener géneros para el cliente {customer_id_test}.")

    print("\n--- Probando get_popular_movies_by_genres (genres=genres, exclude_film_titles=watched_movies) ---")
    if genres and watched_movies:
        recommended_movies_genre = db_service.get_popular_movies_by_genres(genres, watched_movies)
        if recommended_movies_genre:
            print("Películas recomendadas por género:")
            for movie in recommended_movies_genre:
                print(f"- {movie}")
        else:
            print("No se encontraron películas recomendadas por género.")
    else:
        print("No hay suficientes datos para generar recomendaciones por género.")

    print("\n--- Probando get_recommended_movies_by_actor_affinity (customer_id=1, exclude_film_titles=watched_movies) ---")
    if watched_movies:
        recommended_movies_actor = db_service.get_recommended_movies_by_actor_affinity(customer_id_test, watched_movies)
        if recommended_movies_actor:
            print("Películas recomendadas por afinidad de actor:")
            for movie in recommended_movies_actor:
                print(f"- {movie}")
        else:
            print("No se encontraron películas recomendadas por afinidad de actor.")
    else:
        print("No hay películas vistas para generar recomendaciones por afinidad de actor.")
