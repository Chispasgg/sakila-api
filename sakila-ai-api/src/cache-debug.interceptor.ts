import {
  CallHandler,
  ExecutionContext,
  Injectable,
  NestInterceptor,
  Inject,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';

@Injectable()
export class CacheDebugInterceptor implements NestInterceptor {
  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}

  async intercept(context: ExecutionContext, next: CallHandler): Promise<Observable<any>> {
    const request = context.switchToHttp().getRequest();
    const cacheKey = this.generateCacheKey(request);
    
    console.log(`🔍 [CACHE DEBUG] Checking cache for key: ${cacheKey}`);
    
    try {
      const cachedResult = await this.cacheManager.get(cacheKey);
      if (cachedResult) {
        console.log(`✅ [CACHE HIT] Found cached data for: ${cacheKey}`);
      } else {
        console.log(`❌ [CACHE MISS] No cached data for: ${cacheKey}`);
      }
    } catch (error) {
      console.error(`💥 [CACHE ERROR] Error checking cache for key ${cacheKey}:`, error);
    }

    return next.handle().pipe(
      tap(async (data) => {
        try {
          // Verificar si los datos se almacenaron en cache después de la respuesta
          const newCachedResult = await this.cacheManager.get(cacheKey);
          if (newCachedResult) {
            console.log(`💾 [CACHE STORE] Data stored in cache for: ${cacheKey}`);
          } else {
            console.log(`⚠️ [CACHE WARNING] Data not stored in cache for: ${cacheKey}`);
          }
        } catch (error) {
          console.error(`💥 [CACHE ERROR] Error verifying cache storage:`, error);
        }
      }),
    );
  }

  private generateCacheKey(request: any): string {
    return `${request.method}:${request.url}`;
  }
}
