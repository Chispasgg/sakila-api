import { Test, TestingModule } from '@nestjs/testing';
import { RecommendationsController } from './recommendations.controller';
import { RecommendationsV2Service } from './recommendations-v2.service';
import { CacheInterceptor, CacheTTL, CACHE_MANAGER } from '@nestjs/cache-manager';
import { ApiQuery } from '@nestjs/swagger';
import { Reflector } from '@nestjs/core';
import { CustomersService } from '../customers/customers.service';
import { ExternalRecommendationsService } from '../external-recommendations/external-recommendations.service';

describe('RecommendationsController', () => {
  let controller: RecommendationsController;
  let recommendationsV2Service: RecommendationsV2Service;
  let customersService: CustomersService;
  let externalRecommendationsService: ExternalRecommendationsService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [RecommendationsController],
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
          provide: RecommendationsV2Service,
          useValue: {
            getRecommendations: jest.fn(),
          },
        },
        {
          provide: CustomersService,
          useValue: {
            getRecommendationsBasedOnClientRentalCategories: jest.fn(),
            getRecommendationFocusOptions: jest.fn(),
          },
        },
        {
          provide: ExternalRecommendationsService,
          useValue: {
            getRecommendationsFromExternalApi: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get<RecommendationsController>(RecommendationsController);
    recommendationsV2Service = module.get<RecommendationsV2Service>(RecommendationsV2Service);
    customersService = module.get<CustomersService>(CustomersService);
    externalRecommendationsService = module.get<ExternalRecommendationsService>(ExternalRecommendationsService);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  describe('getRecommendationsV2', () => {
    it('should return v2 recommendations', async () => {
      const customerId = 1;
      const result = [{ film_id: 1, title: 'Film A' }];
      jest.spyOn(recommendationsV2Service, 'getRecommendations').mockResolvedValue(result);

      expect(await controller.getRecommendationsV2(customerId)).toBe(result);
      expect(recommendationsV2Service.getRecommendations).toHaveBeenCalledWith(customerId, undefined);
    });

    it('should return v2 recommendations with focus', async () => {
      const customerId = 1;
      const focus = 'actors';
      const result = [{ film_id: 2, title: 'Film B' }];
      jest.spyOn(recommendationsV2Service, 'getRecommendations').mockResolvedValue(result);

      expect(await controller.getRecommendationsV2(customerId, focus)).toBe(result);
      expect(recommendationsV2Service.getRecommendations).toHaveBeenCalledWith(customerId, focus);
    });
  });

  describe('getRecommendationsBasedOnClientRentalCategories', () => {
    it('should return v1 recommendations', async () => {
      const customerId = 1;
      const result = { customer_id: customerId, recommendations: [], explanation: 'Test explanation' };
      jest.spyOn(customersService, 'getRecommendationsBasedOnClientRentalCategories').mockResolvedValue(result);

      expect(await controller.getRecommendationsBasedOnClientRentalCategories(customerId)).toBe(result);
      expect(customersService.getRecommendationsBasedOnClientRentalCategories).toHaveBeenCalledWith(customerId, undefined);
    });

    it('should return v1 recommendations with focus', async () => {
      const customerId = 1;
      const focus = 'genres';
      const result = { customer_id: customerId, recommendations: [], explanation: 'Test explanation' };
      jest.spyOn(customersService, 'getRecommendationsBasedOnClientRentalCategories').mockResolvedValue(result);

      expect(await controller.getRecommendationsBasedOnClientRentalCategories(customerId, focus)).toBe(result);
      expect(customersService.getRecommendationsBasedOnClientRentalCategories).toHaveBeenCalledWith(customerId, focus);
    });
  });

  describe('getExternalRecommendations', () => {
    it('should return external recommendations', async () => {
      const customerId = 1;
      const result = [{ film_id: 3, title: 'Film C' }];
      jest.spyOn(externalRecommendationsService, 'getRecommendationsFromExternalApi').mockResolvedValue(result);

      expect(await controller.getExternalRecommendations(customerId)).toBe(result);
      expect(externalRecommendationsService.getRecommendationsFromExternalApi).toHaveBeenCalledWith(customerId, undefined);
    });

    it('should return external recommendations with focus', async () => {
      const customerId = 1;
      const focus = 'actors';
      const result = [{ film_id: 4, title: 'Film D' }];
      jest.spyOn(externalRecommendationsService, 'getRecommendationsFromExternalApi').mockResolvedValue(result);

      expect(await controller.getExternalRecommendations(customerId, focus)).toBe(result);
      expect(externalRecommendationsService.getRecommendationsFromExternalApi).toHaveBeenCalledWith(customerId, focus);
    });
  });

  describe('getRecommendationFocusOptions', () => {
    it('should return focus options', async () => {
      const result = ['categories', 'actors'];
      jest.spyOn(customersService, 'getRecommendationFocusOptions').mockReturnValue(result);

      expect(controller.getRecommendationFocusOptions()).toBe(result);
      expect(customersService.getRecommendationFocusOptions).toHaveBeenCalled();
    });
  });
});
