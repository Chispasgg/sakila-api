import { CallHandler, ExecutionContext, Injectable, NestInterceptor } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  constructor(private readonly debugMode: boolean) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    if (!this.debugMode) {
      return next.handle();
    }

    const request = context.switchToHttp().getRequest();
    const now = Date.now();

    console.log(`[${new Date().toISOString()}] Request: ${request.method} ${request.url}`);

    return next.handle().pipe(
      tap(() => {
        const response = context.switchToHttp().getResponse();
        console.log(`[${new Date().toISOString()}] Response: ${request.method} ${request.url} - ${response.statusCode} - ${Date.now() - now}ms`);
      }),
    );
  }
}
