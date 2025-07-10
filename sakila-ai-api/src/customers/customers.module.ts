import { Module } from '@nestjs/common';
import { CustomersService } from './customers.service';
import { CustomersController } from './customers.controller';
import { PrismaModule } from '../prisma/prisma.module';
import { ExternalRecommendationsModule } from '../external-recommendations/external-recommendations.module';

@Module({
  imports: [PrismaModule, ExternalRecommendationsModule],
  controllers: [CustomersController],
  providers: [CustomersService],
  exports: [CustomersService], // Export CustomersService so it can be used by other modules
})
export class CustomersModule {}
