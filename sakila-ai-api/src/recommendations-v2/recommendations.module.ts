import { Module } from '@nestjs/common';
import { RecommendationsController } from './recommendations.controller';
import { RecommendationsV2Service } from './recommendations-v2.service';
import { PrismaModule } from '../prisma/prisma.module';
import { CustomersModule } from '../customers/customers.module';
import { ExternalRecommendationsModule } from '../external-recommendations/external-recommendations.module';

@Module({
  imports: [PrismaModule, CustomersModule, ExternalRecommendationsModule],
  controllers: [RecommendationsController],
  providers: [RecommendationsV2Service],
  exports: [RecommendationsV2Service] // Export if needed by other modules
})
export class RecommendationsModule {}
