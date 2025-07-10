import * as request from 'supertest';

describe('CustomersController (Live Server)', () => {
  const appUrl = 'http://localhost:3000';
  const customerId = 1; // Assuming customer with ID 1 exists in Sakila DB
  const nonExistentCustomerId = 99999;

  describe('GET /customers/:id/dashboard', () => {
    it('should return customer dashboard for a valid ID', async () => {
      const response = await request(appUrl)
        .get(`/customers/${customerId}/dashboard`)
        .expect(200);

      expect(response.body).toHaveProperty('customer_id', customerId);
      expect(response.body).toHaveProperty('dashboard');
      expect(response.body.dashboard).toHaveProperty('total_spent');
      expect(response.body.dashboard).toHaveProperty('total_rentals');
    });

    it('should return 404 for a non-existent customer ID', () => {
      return request(appUrl)
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

      const response = await request(appUrl)
        .post('/customers/feedback')
        .send(feedbackDto)
        .expect(201); // 201 Created

      expect(response.text).toBe('Feedback received and stored successfully!');
    });

    it('should return 500 for invalid feedback data', () => {
      const invalidFeedbackDto = {
        userId: 'invalid', // Invalid type
        recommendationType: 'v2',
        isPositive: true,
      };
      return request(appUrl)
        .post('/customers/feedback')
        .send(invalidFeedbackDto)
        .expect(500);
    });
  });

  describe('GET /customers/:id/feedback', () => {
    it('should return feedback for a valid customer ID', async () => {
      const response = await request(appUrl)
        .get(`/customers/${customerId}/feedback`)
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
      expect(response.body.length).toBeGreaterThanOrEqual(0);
    });

    it('should return 404 for a non-existent customer ID when getting feedback', () => {
      const nonExistentCustomerId = 99999;
      return request(appUrl)
        .get(`/customers/${nonExistentCustomerId}/feedback`)
        .expect(404);
    });
  });
});
