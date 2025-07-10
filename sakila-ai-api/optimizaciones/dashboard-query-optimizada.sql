-- Ejemplo de consulta consolidada para dashboard
WITH customer_metrics AS (
  SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    COUNT(DISTINCT r.rental_id) as total_rentals,
    SUM(p.amount) as total_spent,
    MAX(r.rental_date) as last_rental_date
  FROM customer c
  LEFT JOIN rental r ON c.customer_id = r.customer_id
  LEFT JOIN payment p ON r.rental_id = p.rental_id
  WHERE c.customer_id = $1
  GROUP BY c.customer_id, c.first_name, c.last_name, c.email
),
category_preferences AS (
  SELECT 
    cat.name as category_name,
    COUNT(*) as rental_count
  FROM rental r
  JOIN inventory i ON r.inventory_id = i.inventory_id
  JOIN film f ON i.film_id = f.film_id
  JOIN film_category fc ON f.film_id = fc.film_id
  JOIN category cat ON fc.category_id = cat.category_id
  WHERE r.customer_id = $1
  GROUP BY cat.category_id, cat.name
  ORDER BY rental_count DESC
  LIMIT 5
)
-- ... más CTEs para actores, idiomas, etc.
SELECT * FROM customer_metrics;
