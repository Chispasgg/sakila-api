import * as request from 'supertest';

describe('AppController (Live Server)', () => {
  const appUrl = 'http://localhost:3000';

  it('/ (GET)', () => {
    return request(appUrl)
      .get('/')
      .expect(200)
      .expect((res) => {
        expect(res.body).toHaveProperty('status', true);
        expect(res.body).toHaveProperty('date');
      });
  });
});
