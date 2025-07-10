import { Controller, Get, Param, ParseIntPipe, Query, UseInterceptors } from '@nestjs/common';
import { RecommendationsV2Service } from './recommendations-v2.service';
import { FocusValidationV2Pipe } from './pipes/focus-validation-v2.pipe';
import { CacheInterceptor, CacheTTL } from '@nestjs/cache-manager';
import { ApiQuery } from '@nestjs/swagger';
import { CustomersService } from '../customers/customers.service'; // Import CustomersService
import { ExternalRecommendationsService } from '../external-recommendations/external-recommendations.service'; // Import ExternalRecommendationsService
import { FocusValidationPipe } from '../customers/pipes/focus-validation.pipe'; // Import FocusValidationPipe

@Controller('recomendations')
export class RecommendationsController {
  constructor(
    private readonly recommendationsV2Service: RecommendationsV2Service,
    private readonly customersService: CustomersService, // Inject CustomersService
    private readonly externalRecommendationsService: ExternalRecommendationsService, // Inject ExternalRecommendationsService
  ) {}

  @UseInterceptors(CacheInterceptor)
  @CacheTTL(1800)
  @Get('recommendation-focus-options')
  getRecommendationFocusOptions() {
    return this.customersService.getRecommendationFocusOptions();
  }

  @UseInterceptors(CacheInterceptor)
  @CacheTTL(1800)
  @Get(':id/recommendations-v1')
  getRecommendationsBasedOnClientRentalCategories(
    @Param('id', ParseIntPipe) id: number,
    @Query('focus', FocusValidationPipe) focus?: string,
  ) {
    return this.customersService.getRecommendationsBasedOnClientRentalCategories(id, focus);
  }

  @UseInterceptors(CacheInterceptor)
  @CacheTTL(1800) // Cache for 30 minutes
  @ApiQuery({ name: 'focus', required: false, type: String, enum: ['actors', 'genres', 'language', 'rating'], description: 'Optional focus for recommendations (e.g., actors, genres)' })
  @Get(':id/recommendations-v2')
  async getRecommendationsV2(
    @Param('id', ParseIntPipe) id: number,
    @Query('focus', FocusValidationV2Pipe) focus?: string,
  ) {
    return this.recommendationsV2Service.getRecommendations(id, focus);
  }



  @Get(':id/recommendations-external')
  async getExternalRecommendations(
    @Param('id', ParseIntPipe) id: number,
    @Query('focus', FocusValidationPipe) focus?: string,
  ) {
    return this.externalRecommendationsService.getRecommendationsFromExternalApi(id, focus);
  }

  
}