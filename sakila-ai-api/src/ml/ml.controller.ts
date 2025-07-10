import { Controller, Get, Param, ParseIntPipe, UseInterceptors } from '@nestjs/common';
import { MlService } from './ml.service';
import { CacheInterceptor, CacheTTL } from '@nestjs/cache-manager';
import { ApiOperation, ApiParam, ApiResponse, ApiTags } from '@nestjs/swagger';

@ApiTags('ML Recommendations')
@Controller('ml')
export class MlController {
  constructor(private readonly mlService: MlService) {}

  @UseInterceptors(CacheInterceptor)
  @CacheTTL(1800) // Cache for 30 minutes
  @Get('recommendations/:id')
  @ApiOperation({ 
    summary: 'Get ML-based recommendations for a customer',
    description: 'Returns personalized movie recommendations using hybrid machine learning algorithm (collaborative + content-based filtering)'
  })
  @ApiParam({ 
    name: 'id', 
    type: 'number', 
    description: 'Customer ID', 
    example: 4 
  })
  @ApiResponse({ 
    status: 200, 
    description: 'Successful response with ML recommendations',
    schema: {
      type: 'object',
      properties: {
        customer_id: { type: 'number', example: 4 },
        recommendations: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              film_id: { type: 'number', example: 123 },
              title: { type: 'string', example: 'The Matrix' },
              description: { type: 'string', example: 'A computer hacker learns...' },
              release_year: { type: 'number', example: 1999 },
              rating: { type: 'string', example: 'R' },
              genres: { type: 'array', items: { type: 'string' }, example: ['Action', 'Sci-Fi'] },
              actors: { type: 'array', items: { type: 'string' }, example: ['Keanu Reeves', 'Laurence Fishburne'] },
              ml_score: { type: 'number', example: 8.5 },
              confidence: { type: 'number', example: 0.92 },
              recommendation_reason: { type: 'string', example: 'Hybrid: Users like you also enjoyed similar genres' }
            }
          }
        },
        algorithm: { type: 'string', example: 'hybrid_ml' },
        generated_at: { type: 'string', format: 'date-time' },
        metadata: {
          type: 'object',
          properties: {
            total_recommendations: { type: 'number', example: 12 },
            algorithm_version: { type: 'string', example: '1.0' },
            confidence_threshold: { type: 'number', example: 0.75 }
          }
        }
      }
    }
  })
  @ApiResponse({ 
    status: 404, 
    description: 'Customer not found',
    schema: {
      type: 'object',
      properties: {
        statusCode: { type: 'number', example: 404 },
        message: { type: 'string', example: 'Customer with ID 4 not found' },
        error: { type: 'string', example: 'Not Found' }
      }
    }
  })
  async getRecommendations(@Param('id', ParseIntPipe) customerId: number) {
    return this.mlService.getRecommendations(customerId);
  }
}
