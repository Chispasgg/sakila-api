import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './../src/app.module';

describe('RecommendationsController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  const customerId = 1; // Assuming customer with ID 1 exists in Sakila DB
  const nonExistentCustomerId = 99999;

  describe('GET /recomendations/:id/recommendations-v1', () => {
    it('should return recommendations-v1 for a valid customer ID', async () => {
      const response = await request(app.getHttpServer())
        .get(`/recomendations/${customerId}/recommendations-v1`)
        .expect(200);

      expect(response.body).toHaveProperty('customer_id', customerId);
      expect(response.body).toHaveProperty('recommendations');
      expect(Array.isArray(response.body.recommendations)).toBe(true);
    });

    it('should return recommendations-v1 with focus parameter', async () => {
      const response = await request(app.getHttpServer())
        .get(`/recomendations/${customerId}/recommendations-v1?focus=actors`)
        .expect(200);

      expect(response.body).toHaveProperty('customer_id', customerId);
      expect(response.body).toHaveProperty('recommendations');
      expect(Array.isArray(response.body.recommendations)).toBe(true);
      expect(response.body).toHaveProperty('explanation');
    });

    it('should return 404 for non-existent customer ID', () => {
      return request(app.getHttpServer())
        .get(`/recomendations/${nonExistentCustomerId}/recommendations-v1`)
        .expect(404);
    });
  });

  describe('GET /recomendations/:id/recommendations-external', () => {
    // it('should return external recommendations for a valid customer ID', async () => {
    //   // Note: This test assumes the external API is running at http://localhost:2207
    //   const response = await request(app.getHttpServer())
    //     .get(`/recomendations/${customerId}/recommendations-external`)
    //     .expect(200); // Expect 200 OK now

    //   expect(Array.isArray(response.body)).toBe(true);
    //   // Expect some basic structure from the external API response
    //   if (response.body.length > 0) {
    //     expect(response.body[0]).toHaveProperty('film_id');
    //     expect(response.body[0]).toHaveProperty('title');
    //   }
    // });

    it('should return external recommendations with focus parameter', async () => {
      const response = await request(app.getHttpServer())
        .get(`/recomendations/${customerId}/recommendations-external?focus=actors`)
        .expect(200); // Expect 200 OK now

      expect(typeof response.body).toBe('object');
      expect(response.body).toHaveProperty('recommended_movies');
      expect(Array.isArray(response.body.recommended_movies)).toBe(true);
      if (response.body.recommended_movies.length > 0) {
        expect(response.body.recommended_movies[0]).toHaveProperty('film');
        expect(response.body.recommended_movies[0]).toHaveProperty('reason');
      }
    });

    it('should return an error if external API is not available (or 500)', () => {
      // This test is more about ensuring the endpoint handles external API issues gracefully
      // It might return 500 or a specific error message depending on implementation
      // For now, we expect a successful response if the external API is up.
      // If the external API is down, this test will likely fail with a connection error.
      return request(app.getHttpServer())
        .get(`/recomendations/${nonExistentCustomerId}/recommendations-external`)
        .expect(500); // Assuming 500 if external service is down or customer not found externally
    });
  });

  describe('GET /recomendations/recommendation-focus-options', () => {
    it('should return a list of focus options', async () => {
      const response = await request(app.getHttpServer())
        .get('/recomendations/recommendation-focus-options')
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
      expect(response.body).toEqual(expect.arrayContaining(['categories', 'actors', 'languages', 'ratings', 'directors', 'popularity']));
    });
  });

  describe('GET /recomendations/:id/recommendations-v2', () => {
    it('should return recommendations-v2 for a valid customer ID', async () => {
      const response = await request(app.getHttpServer())
        .get(`/recomendations/${customerId}/recommendations-v2`)
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
      expect(response.body.length).toBeLessThanOrEqual(10);
      if (response.body.length > 0) {
        expect(response.body[0]).toHaveProperty('film_id');
        expect(response.body[0]).toHaveProperty('title');
        expect(response.body[0]).toHaveProperty('score');
        expect(response.body[0]).toHaveProperty('explanation');
      }
    });

    it('should return recommendations-v2 with focus parameter', async () => {
      const response = await request(app.getHttpServer())
        .get(`/recomendations/${customerId}/recommendations-v2?focus=actors`)
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
      expect(response.body.length).toBeLessThanOrEqual(10);
      if (response.body.length > 0) {
        expect(response.body[0]).toHaveProperty('film_id');
        expect(response.body[0]).toHaveProperty('title');
        expect(response.body[0]).toHaveProperty('score');
        expect(response.body[0]).toHaveProperty('explanation');
      }
    });

    it('should return 404 for non-existent customer ID', () => {
      return request(app.getHttpServer())
        .get(`/recomendations/${nonExistentCustomerId}/recommendations-v2`)
        .expect(404);
    });

    it('should return 400 for invalid focus parameter', () => {
      return request(app.getHttpServer())
        .get(`/recomendations/${customerId}/recommendations-v2?focus=invalid`)
        .expect(400);
    });
  });
});
