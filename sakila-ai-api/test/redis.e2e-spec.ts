import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './../src/app.module';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';

describe('Redis Caching (e2e)', () => {
  let app: INestApplication;
  let cacheManager: Cache;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    cacheManager = app.get(CACHE_MANAGER);
  });

  afterAll(async () => {
    await cacheManager.del('e2e-test-key'); // Clean up after test
    await app.close();
  });

  it('should be able to set and get a value from Redis', async () => {
    const testKey = 'e2e-test-key';
    const testValue = 'e2e-test-value';
    const ttl = 5; // seconds

    // Set a value in Redis
    await cacheManager.set(testKey, testValue, ttl);

    // Get the value from Redis
    const retrievedValue = await cacheManager.get(testKey);

    // Assert that the retrieved value matches the set value
    expect(retrievedValue).toBe(testValue);
  });

  it('should clear the cache for a key', async () => {
    const testKey = 'e2e-clear-key';
    const testValue = 'value-to-clear';

    await cacheManager.set(testKey, testValue, 10);
    expect(await cacheManager.get(testKey)).toBe(testValue);

    await cacheManager.del(testKey);
    expect(await cacheManager.get(testKey)).toBeUndefined();
  });
});
