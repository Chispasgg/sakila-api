import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { HttpModule } from '@nestjs/axios';
import { ExternalRecommendationsService } from './external-recommendations.service';

@Module({
  imports: [HttpModule, ConfigModule],
  providers: [ExternalRecommendationsService],
  exports: [ExternalRecommendationsService],
})
export class ExternalRecommendationsModule {}
