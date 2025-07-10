import * as request from 'supertest';

describe('MlController (Live Server)', () => {
  const appUrl = 'http://localhost:3000';
  const customerId = 4; // Using customer ID 4 as specified in the curl example
  const nonExistentCustomerId = 99999;

  describe('GET /ml/recommendations/:id', () => {
    it('should return ML recommendations for customer ID 4', async () => {
      const response = await request(appUrl)
        .get(`/ml/recommendations/${customerId}`)
        .expect(200);

      // The external service returns an array of recommendations directly
      expect(Array.isArray(response.body)).toBe(true);
      
      // If recommendations exist, verify their structure
      if (response.body.length > 0) {
        const recommendation = response.body[0];
        expect(recommendation).toHaveProperty('film_id');
        expect(recommendation).toHaveProperty('title');
        expect(recommendation).toHaveProperty('similarity_score');
        expect(recommendation).toHaveProperty('explanation');
        
        // Verify data types
        expect(typeof recommendation.film_id).toBe('number');
        expect(typeof recommendation.title).toBe('string');
        expect(typeof recommendation.similarity_score).toBe('number');
        expect(typeof recommendation.explanation).toBe('string');
        
        // Verify similarity_score is a reasonable value
        expect(recommendation.similarity_score).toBeGreaterThanOrEqual(0);
        expect(recommendation.similarity_score).toBeLessThanOrEqual(1);
        
        console.log(`✓ Found ${response.body.length} recommendations for customer ${customerId}`);
        console.log(`✓ Top recommendation: "${recommendation.title}" (Score: ${recommendation.similarity_score})`);
      } else {
        console.log(`⚠ No recommendations found for customer ${customerId}`);
      }
    });

    it('should return 404 for non-existent customer ID', async () => {
      const response = await request(appUrl)
        .get(`/ml/recommendations/${nonExistentCustomerId}`)
        .expect(404);

      expect(response.body).toHaveProperty('statusCode', 404);
      expect(response.body).toHaveProperty('message');
      expect(response.body.message).toContain('not found');
    });

    it('should return 400 for invalid customer ID format', async () => {
      const response = await request(appUrl)
        .get('/ml/recommendations/invalid')
        .expect(400);

      expect(response.body).toHaveProperty('statusCode', 400);
      expect(response.body).toHaveProperty('message');
    });

    it('should return recommendations with expected structure', async () => {
      const response = await request(appUrl)
        .get(`/ml/recommendations/${customerId}`)
        .expect(200);

      if (response.body.length > 0) {
        response.body.forEach((rec: any) => {
          expect(rec).toHaveProperty('film_id');
          expect(rec).toHaveProperty('title'); 
          expect(rec).toHaveProperty('similarity_score');
          expect(rec).toHaveProperty('explanation');
          
          // Verify explanation contains expected text
          expect(rec.explanation).toContain('Recomendado por similitud');
        });
      }
    });

    it('should return recommendations with similarity scores', async () => {
      const response = await request(appUrl)
        .get(`/ml/recommendations/${customerId}`)
        .expect(200);

      if (response.body.length > 0) {
        response.body.forEach((rec: any) => {
          expect(rec.similarity_score).toBeGreaterThan(0);
          expect(rec.similarity_score).toBeLessThanOrEqual(1);
        });
      }
    });

    it('should handle multiple requests successfully', async () => {
      // First request
      const start1 = Date.now();
      await request(appUrl)
        .get(`/ml/recommendations/${customerId}`)
        .expect(200);
      const duration1 = Date.now() - start1;

      // Second request
      const start2 = Date.now();
      const response2 = await request(appUrl)
        .get(`/ml/recommendations/${customerId}`)
        .expect(200);
      const duration2 = Date.now() - start2;

      // Both should be successful and return arrays
      expect(Array.isArray(response2.body)).toBe(true);
      
      // Requests should complete within reasonable time
      expect(duration2).toBeLessThan(30000); // 30 second max
    });
  });
});
