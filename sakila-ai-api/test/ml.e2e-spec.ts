import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { App } from 'supertest/types';
import { AppModule } from '../src/app.module';

describe('MlController (e2e)', () => {
  let app: INestApplication<App>;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterEach(async () => {
    await app.close();
  });

  describe('GET /ml/recommendations/:id', () => {
    it('should return ML recommendations for a valid customer ID', () => {
      const customerId = 1; // Assuming customer with ID 1 exists in test DB
      return request(app.getHttpServer())
        .get(`/ml/recommendations/${customerId}`)
        .expect(200)
        .expect((res) => {
          // The external service returns an array of recommendations directly
          expect(Array.isArray(res.body)).toBe(true);
          
          // Check recommendation structure if any recommendations exist
          if (res.body.length > 0) {
            const recommendation = res.body[0];
            expect(recommendation).toHaveProperty('film_id');
            expect(recommendation).toHaveProperty('title');
            expect(recommendation).toHaveProperty('similarity_score');
            expect(recommendation).toHaveProperty('explanation');
            expect(typeof recommendation.film_id).toBe('number');
            expect(typeof recommendation.title).toBe('string');
            expect(typeof recommendation.similarity_score).toBe('number');
            expect(typeof recommendation.explanation).toBe('string');
          }
        });
    });

    it('should return 404 for non-existent customer ID', () => {
      const nonExistentCustomerId = 99999;
      return request(app.getHttpServer())
        .get(`/ml/recommendations/${nonExistentCustomerId}`)
        .expect(404)
        .expect((res) => {
          expect(res.body).toHaveProperty('statusCode', 404);
          expect(res.body).toHaveProperty('message');
          expect(res.body.message).toContain('not found');
        });
    });

    it('should return 400 for invalid customer ID format', () => {
      return request(app.getHttpServer())
        .get('/ml/recommendations/invalid')
        .expect(400)
        .expect((res) => {
          expect(res.body).toHaveProperty('statusCode', 400);
          expect(res.body).toHaveProperty('message');
        });
    });

    it('should return consistent response structure', () => {
      const customerId = 1;
      return request(app.getHttpServer())
        .get(`/ml/recommendations/${customerId}`)
        .expect(200)
        .expect((res) => {
          // Verify the response is an array
          expect(Array.isArray(res.body)).toBe(true);
          
          // If there are recommendations, verify structure
          if (res.body.length > 0) {
            res.body.forEach((recommendation: any) => {
              expect(recommendation).toEqual(
                expect.objectContaining({
                  film_id: expect.any(Number),
                  title: expect.any(String),
                  similarity_score: expect.any(Number),
                  explanation: expect.any(String),
                }),
              );
            });
          }
        });
    });

    it('should handle external ML service responses', () => {
      const customerId = 1;
      return request(app.getHttpServer())
        .get(`/ml/recommendations/${customerId}`)
        .expect(200)
        .expect((res) => {
          // The response should be an array (even if empty)
          expect(Array.isArray(res.body)).toBe(true);
          
          // Each recommendation should have the expected structure
          res.body.forEach((rec: any) => {
            expect(rec).toHaveProperty('film_id');
            expect(rec).toHaveProperty('title');
            expect(rec).toHaveProperty('similarity_score');
            expect(rec).toHaveProperty('explanation');
          });
        });
    });
  });
});
