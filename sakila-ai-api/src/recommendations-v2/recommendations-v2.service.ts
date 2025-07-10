import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { Prisma } from '@prisma/client';

@Injectable()
export class RecommendationsV2Service {
  constructor(private prisma: PrismaService) {}

  async getRecommendations(
    customerId: number,
    focus?: string,
  ): Promise<any[]> {
    const customer = await this.prisma.customer.findUnique({
      where: { customer_id: customerId },
    });

    if (!customer) {
      throw new NotFoundException(`Customer with ID ${customerId} not found`);
    }

    // Base weights
    let weights = {
      category: 4,
      actor: 3,
      language: 2,
      rating: 1,
    };

    // Adjust weights based on focus parameter
    if (focus) {
      switch (focus) {
        case 'genres':
          weights.category += 2; // Increase weight for categories
          break;
        case 'actors':
          weights.actor += 2; // Increase weight for actors
          break;
        case 'language':
          weights.language += 2; // Increase weight for language
          break;
        case 'rating':
          weights.rating += 2; // Increase weight for rating
          break;
        default:
          // No change for unknown focus, or handle as an error if strict validation is needed
          break;
      }
    }

    // Get films already rented by the customer
    const rentedFilmIds = await this.prisma.rental.findMany({
      where: { customer_id: customerId },
      select: { inventory: { select: { film_id: true } } },
    });
    const excludedFilmIds = rentedFilmIds.map((r) => r.inventory.film_id);

    // Build the SQL query for recommendations
    const recommendations = await this.prisma.$queryRaw<any[]>(Prisma.sql`
      WITH CustomerPreferences AS (
          SELECT
              fc.category_id AS id,
              'category' AS type,
              COUNT(*) AS count
          FROM rental r
          JOIN inventory i ON r.inventory_id = i.inventory_id
          JOIN film f ON i.film_id = f.film_id
          JOIN film_category fc ON f.film_id = fc.film_id
          WHERE r.customer_id = ${customerId}
          GROUP BY fc.category_id

          UNION ALL

          SELECT
              fa.actor_id AS id,
              'actor' AS type,
              COUNT(*) AS count
          FROM rental r
          JOIN inventory i ON r.inventory_id = i.inventory_id
          JOIN film f ON i.film_id = f.film_id
          JOIN film_actor fa ON f.film_id = fa.film_id
          WHERE r.customer_id = ${customerId}
          GROUP BY fa.actor_id

          UNION ALL

          SELECT
              f.language_id AS id,
              'language' AS type,
              COUNT(*) AS count
          FROM rental r
          JOIN inventory i ON r.inventory_id = i.inventory_id
          JOIN film f ON i.film_id = f.film_id
          WHERE r.customer_id = ${customerId}
          GROUP BY f.language_id

          UNION ALL

          SELECT
              CASE f.rating
                  WHEN 'G' THEN 1
                  WHEN 'PG' THEN 2
                  WHEN 'PG-13' THEN 3
                  WHEN 'R' THEN 4
                  WHEN 'NC-17' THEN 5
                  ELSE 0
              END AS id, -- Convert rating enum to integer for consistent ID type
              'rating' AS type,
              COUNT(*) AS count
          FROM rental r
          JOIN inventory i ON r.inventory_id = i.inventory_id
          JOIN film f ON i.film_id = f.film_id
          WHERE r.customer_id = ${customerId} AND f.rating IS NOT NULL
          GROUP BY f.rating
      ),
      FilmScores AS (
          SELECT
              f.film_id,
              f.title,
              f.description,
              f.release_year,
              f.rating,
              f.language_id,
              -- Calculate score components
              COALESCE(SUM(cp.count * ${weights.category}) FILTER (WHERE cp.type = 'category' AND fc.category_id = cp.id), 0) AS category_score,
              COALESCE(SUM(cp.count * ${weights.actor}) FILTER (WHERE cp.type = 'actor' AND fa.actor_id = cp.id), 0) AS actor_score,
              COALESCE(SUM(cp.count * ${weights.language}) FILTER (WHERE cp.type = 'language' AND f.language_id = cp.id), 0) AS language_score,
              COALESCE(SUM(cp.count * ${weights.rating}) FILTER (WHERE cp.type = 'rating' AND (CASE f.rating WHEN 'G' THEN 1 WHEN 'PG' THEN 2 WHEN 'PG-13' THEN 3 WHEN 'R' THEN 4 WHEN 'NC-17' THEN 5 ELSE 0 END) = cp.id), 0) AS rating_score
          FROM film f
          LEFT JOIN film_category fc ON f.film_id = fc.film_id
          LEFT JOIN film_actor fa ON f.film_id = fa.film_id
          LEFT JOIN CustomerPreferences cp ON
              (cp.type = 'category' AND fc.category_id = cp.id) OR
              (cp.type = 'actor' AND fa.actor_id = cp.id) OR
              (cp.type = 'language' AND f.language_id = cp.id) OR
              (cp.type = 'rating' AND (CASE f.rating WHEN 'G' THEN 1 WHEN 'PG' THEN 2 WHEN 'PG-13' THEN 3 WHEN 'R' THEN 4 WHEN 'NC-17' THEN 5 ELSE 0 END) = cp.id)
          WHERE f.film_id NOT IN (${Prisma.join(excludedFilmIds.length > 0 ? excludedFilmIds : [0])})
          GROUP BY f.film_id, f.title, f.description, f.release_year, f.rating, f.language_id
      )
      SELECT
          fs.film_id,
          fs.title,
          fs.description,
          fs.release_year,
          (SELECT ARRAY_AGG(c.name) FROM film_category fcat JOIN category c ON fcat.category_id = c.category_id WHERE fcat.film_id = fs.film_id) AS genres,
          (SELECT ARRAY_AGG(a.first_name || ' ' || a.last_name) FROM film_actor fact JOIN actor a ON fact.actor_id = a.actor_id WHERE fact.film_id = fs.film_id) AS actors,
          -- Recalculate customer_rentals_by_genre_count and customer_rentals_by_actor_count for explanation
          (SELECT COUNT(DISTINCT r_cust.rental_id)::int
           FROM rental r_cust
           JOIN inventory i_cust ON r_cust.inventory_id = i_cust.inventory_id
           JOIN film f_cust ON i_cust.film_id = f_cust.film_id
           JOIN film_category fc_cust ON f_cust.film_id = fc_cust.film_id
           WHERE r_cust.customer_id = ${customerId}
           AND fc_cust.category_id IN (
               SELECT fc_rec.category_id
               FROM film_category fc_rec
               WHERE fc_rec.film_id = fs.film_id
           )
          ) AS customer_rentals_by_genre_count,
          (SELECT COUNT(DISTINCT r_cust.rental_id)::int
           FROM rental r_cust
           JOIN inventory i_cust ON r_cust.inventory_id = i_cust.inventory_id
           JOIN film f_cust ON i_cust.film_id = f_cust.film_id
           JOIN film_actor fa_cust ON f_cust.film_id = fa_cust.film_id
           WHERE r_cust.customer_id = ${customerId}
           AND fa_cust.actor_id IN (
               SELECT fa_rec.actor_id
               FROM film_actor fa_rec
               WHERE fa_rec.film_id = fs.film_id
           )
          ) AS customer_rentals_by_actor_count,
          (fs.category_score + fs.actor_score + fs.language_score + fs.rating_score) AS score,
          -- Generate explanation
          CASE
              WHEN fs.category_score > 0 AND fs.actor_score > 0 THEN 'Based on your interest in similar genres and actors.'
              WHEN fs.category_score > 0 THEN 'Based on your interest in similar genres.'
              WHEN fs.actor_score > 0 THEN 'Based on your interest in similar actors.'
              WHEN fs.language_score > 0 THEN 'Based on your interest in similar languages.'
              WHEN fs.rating_score > 0 THEN 'Based on your interest in similar film ratings.'
              ELSE 'Recommended based on general relevance.'
          END AS explanation
      FROM FilmScores fs
      ORDER BY score DESC
      LIMIT 10;
    `);

    return recommendations;
  }
}
