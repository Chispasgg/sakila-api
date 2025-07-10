import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { Prisma } from '@prisma/client';
import { CreateFeedbackDto } from './dto/create-feedback.dto';

@Injectable()
export class CustomersService {
  constructor(private prisma: PrismaService) {}

  async getDashboard(id: number) {
    const customer = await this.prisma.customer.findUnique({
      where: { customer_id: id },
      select: {
        customer_id: true,
        first_name: true,
        last_name: true,
        email: true,
      },
    });

    if (!customer) {
      throw new NotFoundException(`Customer with ID ${id} not found`);
    }

    // Consultas de agregación
    const totalSpent = await this.getTotalSpent(id);
    const totalRentals = await this.getRentalCount(id);
    const averageRating = await this.getAverageRatingOfRentedFilms(id);
    const lastRental = await this.getLastRental(id);
    const overdueReturns = await this.getLateReturnsCount(id);
    const topCategories = await this.getTopCategories(id);
    const topActors = await this.getTopActors(id);
    const topLanguages = await this.getTopLanguages(id);

    return {
      ...customer,
      dashboard: {
        most_rented_categories: topCategories,
        most_rented_actors: topActors,
        most_rented_languages: topLanguages,
        total_spent: totalSpent,
        total_rentals: totalRentals,
        average_rating_of_films_rented: averageRating,
        last_rental_info: lastRental,
        number_of_overdue_returns: overdueReturns,
        links: {
          recommendations_based_on_client_rental_categories: `/customers/${id}/recommendations_based_on_client_rental_categories`,
        },
      },
    };
  }

  async submitFeedback(feedbackDto: CreateFeedbackDto): Promise<string> {
    try {
      await this.prisma.feedback.create({
        data: {
          user_id: feedbackDto.userId,
          recommendation_type: feedbackDto.recommendationType,
          feedback_text: feedbackDto.feedbackText,
          is_positive: feedbackDto.isPositive,
        },
      });
      return 'Feedback received and stored successfully!';
    } catch (error) {
      console.error('Error storing feedback:', error);
      throw new Error('Failed to store feedback.');
    }
  }

  private async getTotalSpent(customerId: number): Promise<number> {
    const result = await this.prisma.payment.aggregate({
      _sum: {
        amount: true,
      },
      where: {
        customer_id: customerId,
      },
    });
    return result._sum.amount?.toNumber() || 0;
  }

  private async getRentalCount(customerId: number): Promise<number> {
    return this.prisma.rental.count({ where: { customer_id: customerId } });
  }

  private async getLastRental(customerId: number): Promise<any> {
    return this.prisma.rental.findFirst({
      where: { customer_id: customerId },
      orderBy: { rental_date: 'desc' },
      include: { inventory: { include: { film: true } } },
    });
  }

  private async getLateReturnsCount(customerId: number): Promise<number> {
    const rentals = await this.prisma.rental.findMany({
        where: { 
            customer_id: customerId,
            return_date: { not: null }
        },
        include: { inventory: { include: { film: true } } }
    });

    let lateCount = 0;
    for (const rental of rentals) {
        const rentalDuration = rental.inventory.film.rental_duration;
        const rentedAt = rental.rental_date.getTime();
        const returnedAt = rental.return_date!.getTime();
        const durationInDays = (returnedAt - rentedAt) / (1000 * 3600 * 24);

        if (durationInDays > rentalDuration) {
            lateCount++;
        }
    }
    return lateCount;
  }

  private async getTopCategories(customerId: number): Promise<any> {
    return this.prisma.$queryRaw`
      SELECT c.name, COUNT(*)::int as count
      FROM rental r
      JOIN inventory i ON r.inventory_id = i.inventory_id
      JOIN film_category fc ON i.film_id = fc.film_id
      JOIN category c ON fc.category_id = c.category_id
      WHERE r.customer_id = ${customerId}
      GROUP BY c.name
      ORDER BY count DESC
      LIMIT 5;
    `;
  }

  private async getTopActors(customerId: number): Promise<any> {
    return this.prisma.$queryRaw`
      SELECT a.actor_id, a.first_name, a.last_name, COUNT(*)::int as count
      FROM rental r
      JOIN inventory i ON r.inventory_id = i.inventory_id
      JOIN film_actor fa ON i.film_id = fa.film_id
      JOIN actor a ON fa.actor_id = a.actor_id
      WHERE r.customer_id = ${customerId}
      GROUP BY a.actor_id, a.first_name, a.last_name
      ORDER BY count DESC
      LIMIT 5;
    `;
  }

  private async getTopLanguages(customerId: number): Promise<any> {
    return this.prisma.$queryRaw`
      SELECT TRIM(l.name) as name, COUNT(*)::int as count
      FROM rental r
      JOIN inventory i ON r.inventory_id = i.inventory_id
      JOIN film f ON i.film_id = f.film_id
      JOIN language l ON f.language_id = l.language_id
      WHERE r.customer_id = ${customerId}
      GROUP BY TRIM(l.name)
      ORDER BY count DESC
      LIMIT 3;
    `;
  }

  private async getTopRatings(customerId: number): Promise<any> {
    return this.prisma.$queryRaw`
      SELECT f.rating, COUNT(*)::int as count
      FROM rental r
      JOIN inventory i ON r.inventory_id = i.inventory_id
      JOIN film f ON i.film_id = f.film_id
      WHERE r.customer_id = ${customerId} AND f.rating IS NOT NULL
      GROUP BY f.rating
      ORDER BY count DESC
      LIMIT 3;
    `;
  }

  private async getTopDirectors(customerId: number): Promise<any> {
    // Sakila no tiene una tabla de directores directamente ligada a film
    // Por ahora, devolveremos un placeholder.
    return []; 
  }

  private async getAverageRatingOfRentedFilms(customerId: number): Promise<number> {
    const result = await this.prisma.$queryRaw`
      SELECT AVG(
          CASE f.rating
              WHEN 'G' THEN 1
              WHEN 'PG' THEN 2
              WHEN 'PG-13' THEN 3
              WHEN 'R' THEN 4
              WHEN 'NC-17' THEN 5
              ELSE 0
          END
      )::numeric(10,2) as average_rating
      FROM rental r
      JOIN inventory i ON r.inventory_id = i.inventory_id
      JOIN film f ON i.film_id = f.film_id
      WHERE r.customer_id = ${customerId};
    ` as any[];
    return result[0]?.average_rating?.toNumber() || 0;
  }

  private async getMostPopularFilms(customerId: number): Promise<any[]> {
    return this.prisma.$queryRaw`
      SELECT
          f.film_id,
          f.title,
          f.description,
          f.release_year,
          (SELECT ARRAY_AGG(c.name) FROM film_category fc2 JOIN category c ON fc2.category_id = c.category_id WHERE fc2.film_id = f.film_id) as genres,
          (SELECT ARRAY_AGG(a.first_name || ' ' || a.last_name) FROM film_actor fa2 JOIN actor a ON fa2.actor_id = a.actor_id WHERE fa2.film_id = f.film_id) as actors,
          (SELECT COUNT(DISTINCT r_cust.rental_id)::int
           FROM rental r_cust
           JOIN inventory i_cust ON r_cust.inventory_id = i_cust.inventory_id
           JOIN film f_cust ON i_cust.film_id = f_cust.film_id
           WHERE r_cust.customer_id = ${customerId}
           AND EXISTS (
               SELECT 1
               FROM film_category fc_rec
               JOIN film_category fc_cust ON fc_rec.category_id = fc_cust.category_id
               WHERE fc_rec.film_id = f.film_id AND fc_cust.film_id = f_cust.film_id
           )
          ) as customer_rentals_by_genre_count,
          (SELECT COUNT(DISTINCT r_cust.rental_id)::int
           FROM rental r_cust
           JOIN inventory i_cust ON r_cust.inventory_id = i_cust.inventory_id
           JOIN film f_cust ON i_cust.film_id = f_cust.film_id
           JOIN film_actor fa_cust ON f_cust.film_id = fa_cust.film_id
           WHERE r_cust.customer_id = ${customerId}
           AND EXISTS (
               SELECT 1
               FROM film_actor fa_rec
               JOIN film_actor fa_cust ON fa_rec.actor_id = fa_cust.actor_id
               WHERE fa_rec.film_id = f.film_id AND fa_cust.film_id = f_cust.film_id
           )
          ) as customer_rentals_by_actor_count,
          COUNT(r.rental_id)::int as popularity_score
      FROM film f
      JOIN inventory i ON f.film_id = i.film_id
      JOIN rental r ON i.inventory_id = r.inventory_id
      WHERE f.film_id NOT IN (
          SELECT i2.film_id
          FROM rental r2
          JOIN inventory i2 ON r2.inventory_id = i2.inventory_id
          WHERE r2.customer_id = ${customerId}
      )
      GROUP BY f.film_id, f.title, f.description, f.release_year
      ORDER BY popularity_score DESC
      LIMIT 10;
    `;
  }

  async getRecommendationsBasedOnClientRentalCategories(id: number, focus?: string) {
    const customer = await this.prisma.customer.findUnique({
      where: { customer_id: id },
    });

    if (!customer) {
      throw new NotFoundException(`Customer with ID ${id} not found`);
    }

    let recommendedFilms: any[] = [];
    let explanation: string = '';

    const baseFilmQuery = (whereClause: Prisma.Sql, joinClause: Prisma.Sql) => Prisma.sql`
        SELECT DISTINCT
            f.film_id,
            f.title,
            f.description,
            f.release_year,
            (SELECT ARRAY_AGG(c.name) FROM film_category fc2 JOIN category c ON fc2.category_id = c.category_id WHERE fc2.film_id = f.film_id) as genres,
            (SELECT ARRAY_AGG(a.first_name || ' ' || a.last_name) FROM film_actor fa2 JOIN actor a ON fa2.actor_id = a.actor_id WHERE fa2.film_id = f.film_id) as actors,
            (SELECT COUNT(DISTINCT r_cust.rental_id)::int
             FROM rental r_cust
             JOIN inventory i_cust ON r_cust.inventory_id = i_cust.inventory_id
             JOIN film f_cust ON i_cust.film_id = f_cust.film_id
             JOIN film_category fc_cust ON f_cust.film_id = fc_cust.film_id
             WHERE r_cust.customer_id = ${id}
             AND fc_cust.category_id IN (
                 SELECT fc_rec.category_id
                 FROM film_category fc_rec
                 WHERE fc_rec.film_id = f.film_id
             )
            ) as customer_rentals_by_genre_count,
            (SELECT COUNT(DISTINCT r_cust.rental_id)::int
             FROM rental r_cust
             JOIN inventory i_cust ON r_cust.inventory_id = i_cust.inventory_id
             JOIN film f_cust ON i_cust.film_id = f_cust.film_id
             JOIN film_actor fa_cust ON f_cust.film_id = fa_cust.film_id
             WHERE r_cust.customer_id = ${id}
             AND fa_cust.actor_id IN (
                 SELECT fa_rec.actor_id
                 FROM film_actor fa_rec
                 WHERE fa_rec.film_id = f.film_id
             )
            ) as customer_rentals_by_actor_count
        FROM film f
        ${joinClause}
        WHERE ${whereClause}
        AND f.film_id NOT IN (
            SELECT i.film_id
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            WHERE r.customer_id = ${id}
        )
        LIMIT 10;
    `;

    if (focus === 'actors') {
      const topActors = await this.getTopActors(id);
      if (topActors.length === 0) {
        return { message: `No recommendations available for customer ${id}. No rental history found.` };
      }

      const actorIds = topActors.map((actor: any) => actor.actor_id);
      recommendedFilms = await this.prisma.$queryRaw(baseFilmQuery(Prisma.sql`fa.actor_id IN (${Prisma.join(actorIds)})`, Prisma.sql`JOIN film_actor fa ON f.film_id = fa.film_id`));
      explanation = `Based on your top rented actors: ${topActors.map((a: any) => `${a.first_name} ${a.last_name}`).join(', ')}`;

    } else if (focus === 'languages') {
      const topLanguages = await this.getTopLanguages(id);
      if (topLanguages.length === 0) {
        return { message: `No recommendations available for customer ${id}. No rental history found.` };
      }

      const languageNames = topLanguages.map((lang: any) => lang.name);
      recommendedFilms = await this.prisma.$queryRaw(baseFilmQuery(Prisma.sql`TRIM(l.name) IN (${Prisma.join(languageNames)})`, Prisma.sql`JOIN language l ON f.language_id = l.language_id`));
      explanation = `Based on your top rented languages: ${languageNames.join(', ')}`;

    } else if (focus === 'ratings') {
      const topRatings = await this.getTopRatings(id);
      if (topRatings.length === 0) {
        return { message: `No recommendations available for customer ${id}. No rental history found.` };
      }

      const ratingNames = topRatings.map((rating: any) => rating.rating);
      recommendedFilms = await this.prisma.$queryRaw(baseFilmQuery(Prisma.sql`f.rating::text IN (${Prisma.join(ratingNames)})`, Prisma.empty));
      explanation = `Based on your top rented ratings: ${ratingNames.join(', ')}`;

    } else if (focus === 'directors') {
      // Director logic is complex due to Sakila schema.
      // The Sakila database does not have a direct 'director' table or a 'director_id' in the 'film' table.
      // Therefore, director-based recommendations cannot be directly implemented with the current schema.
      // To implement this, the database schema would need to be extended with director information.
      recommendedFilms = []; // No films can be recommended based on directors
      explanation = `Director-based recommendations are not directly supported by the current Sakila database schema. To enable this, the schema would need to include director information for films.`;

    } else if (focus === 'popularity') {
      recommendedFilms = await this.getMostPopularFilms(id);
      if (recommendedFilms.length === 0) {
        return { message: `No popular recommendations available for customer ${id}.` };
      }
      explanation = `Based on overall popularity (most rented films, excluding your rentals).`;

    } else { // Default to categories
      const topCategories = await this.getTopCategories(id);
      if (topCategories.length === 0) {
        return { message: `No recommendations available for customer ${id}. No rental history found.` };
      }

      const categoryNames = topCategories.map((cat: any) => cat.name);
      recommendedFilms = await this.prisma.$queryRaw(baseFilmQuery(Prisma.sql`c.name IN (${Prisma.join(categoryNames)})`, Prisma.sql`JOIN film_category fc ON f.film_id = fc.film_id JOIN category c ON fc.category_id = c.category_id`));
      explanation = `Based on your top rented categories: ${categoryNames.join(', ')}`;
    }

    return {
      customer_id: id,
      recommendations: recommendedFilms,
      explanation: explanation,
    };
  }

  public getRecommendationFocusOptions(): string[] {
    return ['categories', 'actors', 'languages', 'ratings', 'directors', 'popularity'];
  }

  async getFeedbackByCustomerId(customerId: number): Promise<any[]> {
    const customerExists = await this.prisma.customer.findUnique({
      where: { customer_id: customerId },
    });

    if (!customerExists) {
      throw new NotFoundException(`Customer with ID ${customerId} not found`);
    }

    return this.prisma.feedback.findMany({
      where: { user_id: customerId },
      orderBy: { created_at: 'desc' },
    });
  }
}