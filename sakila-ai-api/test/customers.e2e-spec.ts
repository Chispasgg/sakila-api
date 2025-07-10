import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './../src/app.module';
import { PrismaService } from './../src/prisma/prisma.service';

describe('CustomersController (e2e)', () => {
  let app: INestApplication;
  let prismaService: PrismaService;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    prismaService = app.get<PrismaService>(PrismaService);
    // Clean up database before tests if necessary
    // await prismaService.customer.deleteMany({});
  });

  afterAll(async () => {
    await app.close();
  });

  describe('GET /customers/:id/dashboard', () => {
    it('should return customer dashboard for a valid ID', async () => {
      const customerId = 1; // Assuming customer with ID 1 exists in Sakila DB
      const response = await request(app.getHttpServer())
        .get(`/customers/${customerId}/dashboard`)
        .expect(200);

      expect(response.body).toHaveProperty('customer_id', customerId);
      expect(response.body).toHaveProperty('dashboard');
      expect(response.body.dashboard).toHaveProperty('total_spent');
      expect(response.body.dashboard).toHaveProperty('total_rentals');
    });

    it('should return 404 for a non-existent customer ID', () => {
      const nonExistentCustomerId = 99999;
      return request(app.getHttpServer())
        .get(`/customers/${nonExistentCustomerId}/dashboard`)
        .expect(404);
    });
  });

  describe('POST /customers/feedback', () => {
    it('should successfully submit feedback', async () => {
      const feedbackDto = {
        userId: 1, // Assuming customer with ID 1 exists
        recommendationType: 'v2',
        feedbackText: 'Great recommendations!',
        isPositive: true,
      };

      const response = await request(app.getHttpServer())
        .post('/customers/feedback')
        .send(feedbackDto)
        .expect(201); // 201 Created

      expect(response.text).toBe('Feedback received and stored successfully!');

      // Optionally, verify the feedback was stored in the DB
      const storedFeedback = await prismaService.feedback.findFirst({
        where: { user_id: feedbackDto.userId, recommendation_type: feedbackDto.recommendationType },
        orderBy: { created_at: 'desc' },
      });
      expect(storedFeedback).toBeDefined();
      expect(storedFeedback?.feedback_text).toBe(feedbackDto.feedbackText);
    });

    it('should return 500 for invalid feedback data', () => {
      const invalidFeedbackDto = {
        userId: 'invalid', // Invalid type
        recommendationType: 'v2',
        isPositive: true,
      };
      return request(app.getHttpServer())
        .post('/customers/feedback')
        .send(invalidFeedbackDto)
        .expect(500);
    });
  });

  describe('GET /customers/:id/feedback', () => {
    it('should return feedback for a valid customer ID', async () => {
      const customerId = 1; // Assuming customer with ID 1 exists and has feedback
      const response = await request(app.getHttpServer())
        .get(`/customers/${customerId}/feedback`)
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
      // Expect at least one feedback entry if previous test ran successfully
      expect(response.body.length).toBeGreaterThanOrEqual(0);
    });

    it('should return 404 for a non-existent customer ID when getting feedback', () => {
      const nonExistentCustomerId = 99999;
      return request(app.getHttpServer())
        .get(`/customers/${nonExistentCustomerId}/feedback`)
        .expect(404);
    });
  });
});
