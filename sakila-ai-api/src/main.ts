import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { PrismaService } from './prisma/prisma.service';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { LoggingInterceptor } from './logging.interceptor'; // Importar el interceptor

// Add this to handle BigInt serialization issues with JSON.stringify
(BigInt.prototype as any).toJSON = function() {
  return Number(this);
};

const DEBUG_MODE = process.env.DEBUG_MODE === 'true' || false; // Variable global de depuración desde ENV

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const prismaService = app.get(PrismaService);
  await prismaService.enableShutdownHooks(app);

  app.useGlobalInterceptors(new LoggingInterceptor(DEBUG_MODE)); // Aplicar el interceptor globalmente

  const config = new DocumentBuilder()
    .setTitle('Sakila AI Recommendation Engine API')
    .setDescription('API para el motor de recomendaciones de Sakila')
    .setVersion('1.0')
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);

  await app.listen(3000);
}
bootstrap();
