import { Test, TestingModule } from '@nestjs/testing';
import { MlController } from './ml.controller';
import { MlService } from './ml.service';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Reflector } from '@nestjs/core';

describe('MlController', () => {
  let controller: MlController;
  let service: MlService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [MlController],
      providers: [
        {
          provide: CACHE_MANAGER,
          useValue: {
            get: jest.fn(),
            set: jest.fn(),
            del: jest.fn(),
          },
        },
        Reflector,
        {
          provide: MlService,
          useValue: {
            getRecommendations: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get<MlController>(MlController);
    service = module.get<MlService>(MlService);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  describe('getRecommendations', () => {
    it('should return ML recommendations for a valid customer ID', async () => {
      const customerId = 4;
      const mockResult = {
        customer_id: customerId,
        recommendations: [
          {
            film_id: 123,
            title: 'Test Movie',
            description: 'A test movie',
            release_year: 2000,
            rating: 'PG-13',
            genres: ['Action', 'Adventure'],
            actors: ['Actor One', 'Actor Two'],
            ml_score: 8.5,
            confidence: 0.92,
            recommendation_reason: 'Hybrid: Users like you also enjoyed similar genres',
          },
        ],
        algorithm: 'hybrid_ml',
        generated_at: new Date().toISOString(),
        metadata: {
          total_recommendations: 1,
          algorithm_version: '1.0',
          confidence_threshold: 0.75,
        },
      };

      jest.spyOn(service, 'getRecommendations').mockResolvedValue(mockResult);

      const result = await controller.getRecommendations(customerId);

      expect(result).toBe(mockResult);
      expect(service.getRecommendations).toHaveBeenCalledWith(customerId);
    });

    it('should pass the customer ID to the service', async () => {
      const customerId = 4;
      const mockResult = {
        customer_id: customerId,
        recommendations: [],
        algorithm: 'hybrid_ml',
        generated_at: new Date().toISOString(),
        metadata: {
          total_recommendations: 0,
          algorithm_version: '1.0',
          confidence_threshold: 0.75,
        },
      };

      jest.spyOn(service, 'getRecommendations').mockResolvedValue(mockResult);

      await controller.getRecommendations(customerId);

      expect(service.getRecommendations).toHaveBeenCalledWith(customerId);
    });
  });
});
