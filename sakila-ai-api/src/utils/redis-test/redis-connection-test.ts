import { NestFactory } from '@nestjs/core';
import { AppModule } from '../../app.module';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';

async function runRedisTest() {
  const app = await NestFactory.createApplicationContext(AppModule);
  const cacheManager = app.get<Cache>(CACHE_MANAGER);

  const testKey = 'standalone-redis-test-key';
  const testValue = 'Hello from Standalone Redis Test!';
  const ttl = 60; // 60 seconds

  // Assuming REDIS_HOST and REDIS_PORT are configured in AppModule's CacheModule
  // For logging, we can try to get them if they are exposed, or just use the configured ones.
  // For this standalone script, we'll rely on the AppModule's configuration.

  console.log(`[Standalone Redis Test] Starting test...`);

  try {
    await cacheManager.set(testKey, testValue, ttl);
    console.log(`[Standalone Redis Test] Successfully set key: ${testKey} with value: ${testValue}`);

    const cachedValue = await cacheManager.get(testKey);
    console.log(`[Standalone Redis Test] Successfully got key: ${testKey} with cached value: ${cachedValue}`);

    if (cachedValue === testValue) {
      console.log(`[Standalone Redis Test] Redis connection and read/write successful!`);
    } else {
      console.log(`[Standalone Redis Test] Redis read/write mismatch. Expected: ${testValue}, Got: ${cachedValue}`);
    }
  } catch (error) {
    console.error(`[Standalone Redis Test] Error connecting to Redis:`, error.message);
  } finally {
    await app.close();
  }
}

runRedisTest();
