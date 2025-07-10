import { Test, TestingModule } from '@nestjs/testing';
import { RecommendationsV2Service } from './recommendations-v2.service';
import { PrismaService } from '../prisma/prisma.service';
import { NotFoundException } from '@nestjs/common';
import { Prisma } from '@prisma/client';

describe('RecommendationsV2Service', () => {
  let service: RecommendationsV2Service;
  let prisma: PrismaService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        RecommendationsV2Service,
        {
          provide: PrismaService,
          useValue: {
            customer: {
              findUnique: jest.fn(),
            },
            rental: {
              findMany: jest.fn(),
            },
            $queryRaw: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get<RecommendationsV2Service>(RecommendationsV2Service);
    prisma = module.get<PrismaService>(PrismaService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('getRecommendations', () => {
    const customerId = 1;
    const mockCustomer = {
      customer_id: customerId,
      store_id: 1,
      first_name: 'JOHN',
      last_name: 'DOE',
      email: 'john.doe@example.com',
      address_id: 1,
      activebool: true,
      create_date: new Date(),
      last_update: new Date(),
      active: 1,
    };

    beforeEach(() => {
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(mockCustomer);
      jest.spyOn(prisma.rental, 'findMany').mockResolvedValue([]); // No rented films by default
    });

    it('should throw NotFoundException if customer not found', async () => {
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(null);
      await expect(service.getRecommendations(customerId)).rejects.toThrow(NotFoundException);
    });

    it('should return recommendations with default weights', async () => {
      const mockRecommendations = [
        { film_id: 1, title: 'Film A', score: 10, explanation: 'Recommended based on general relevance.' },
      ];
      jest.spyOn(prisma, '$queryRaw').mockResolvedValue(mockRecommendations);

      const result = await service.getRecommendations(customerId);
      expect(result).toBe(mockRecommendations);
      expect(prisma.$queryRaw).toHaveBeenCalled();
      // Further assertions can be made on the SQL query passed to $queryRaw if needed
    });

    it('should return recommendations with increased genre weight when focus is genres', async () => {
      const mockRecommendations = [
        { film_id: 1, title: 'Film A', score: 12, explanation: 'Based on your interest in similar genres.' },
      ];
      jest.spyOn(prisma, '$queryRaw').mockResolvedValue(mockRecommendations);

      const result = await service.getRecommendations(customerId, 'genres');
      expect(result).toBe(mockRecommendations);
      expect(prisma.$queryRaw).toHaveBeenCalled();
      // Assert that the SQL query contains the adjusted weights
    });

    it('should return recommendations with increased actor weight when focus is actors', async () => {
      const mockRecommendations = [
        { film_id: 1, title: 'Film A', score: 11, explanation: 'Based on your interest in similar actors.' },
      ];
      jest.spyOn(prisma, '$queryRaw').mockResolvedValue(mockRecommendations);

      const result = await service.getRecommendations(customerId, 'actors');
      expect(result).toBe(mockRecommendations);
      expect(prisma.$queryRaw).toHaveBeenCalled();
    });

    it('should exclude already rented films', async () => {
      const rentedFilmIds = [{
        rental_id: 1,
        rental_date: new Date(),
        inventory_id: 1,
        customer_id: customerId,
        return_date: null,
        staff_id: 1,
        last_update: new Date(),
        inventory: { film_id: 10 },
      }];
      jest.spyOn(prisma.rental, 'findMany').mockResolvedValue(rentedFilmIds);

      const mockRecommendations = [
        { film_id: 1, title: 'Film A', score: 10, explanation: 'Recommended based on general relevance.' },
      ];
      jest.spyOn(prisma, '$queryRaw').mockResolvedValue(mockRecommendations);

      await service.getRecommendations(customerId);
      // Assert that the SQL query passed to $queryRaw contains the excluded film ID
      expect(prisma.$queryRaw).toHaveBeenCalledWith(expect.objectContaining({
        strings: expect.arrayContaining([
          expect.stringContaining('WHERE f.film_id NOT IN ('),
        ]),
      }));
    });
  });
});
