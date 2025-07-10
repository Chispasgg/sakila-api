import { Test, TestingModule } from '@nestjs/testing';
import { CustomersService } from './customers.service';
import { PrismaService } from '../prisma/prisma.service';
import { NotFoundException } from '@nestjs/common';
import { CreateFeedbackDto } from './dto/create-feedback.dto';

describe('CustomersService', () => {
  let service: CustomersService;
  let prisma: PrismaService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        CustomersService,
        {
          provide: PrismaService,
          useValue: {
            customer: {
              findUnique: jest.fn(),
            },
            rental: {
              count: jest.fn(),
              findMany: jest.fn(),
              findFirst: jest.fn(),
            },
            payment: {
              aggregate: jest.fn(),
            },
            feedback: {
              create: jest.fn(),
              findMany: jest.fn(),
            },
            $queryRaw: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get<CustomersService>(CustomersService);
    prisma = module.get<PrismaService>(PrismaService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('getDashboard', () => {
    it('should return a customer dashboard', async () => {
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

      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(mockCustomer);
      jest.spyOn(service as any, 'getTotalSpent').mockResolvedValue(100.50);
      jest.spyOn(service as any, 'getRentalCount').mockResolvedValue(10);
      jest.spyOn(service as any, 'getAverageRatingOfRentedFilms').mockResolvedValue(3.5);
      jest.spyOn(service as any, 'getLastRental').mockResolvedValue({});
      jest.spyOn(service as any, 'getLateReturnsCount').mockResolvedValue(1);
      jest.spyOn(service as any, 'getTopCategories').mockResolvedValue([]);
      jest.spyOn(service as any, 'getTopActors').mockResolvedValue([]);
      jest.spyOn(service as any, 'getTopLanguages').mockResolvedValue([]);

      const result = await service.getDashboard(customerId);

      expect(result).toHaveProperty('customer_id', customerId);
      expect(result).toHaveProperty('dashboard');
      expect(prisma.customer.findUnique).toHaveBeenCalledWith({ where: { customer_id: customerId }, select: expect.any(Object) });
    });

    it('should throw NotFoundException if customer not found', async () => {
      const customerId = 999;
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(null);

      await expect(service.getDashboard(customerId)).rejects.toThrow(NotFoundException);
    });
  });

  describe('submitFeedback', () => {
    it('should create feedback successfully', async () => {
      const feedbackDto: CreateFeedbackDto = {
        userId: 1,
        recommendationType: 'v2',
        feedbackText: 'Great!',
        isPositive: true,
      };
      jest.spyOn(prisma.feedback, 'create').mockResolvedValue(feedbackDto as any);

      const result = await service.submitFeedback(feedbackDto);
      expect(result).toBe('Feedback received and stored successfully!');
      expect(prisma.feedback.create).toHaveBeenCalledWith({ data: feedbackDto });
    });

    it('should throw an error if feedback creation fails', async () => {
      const feedbackDto: CreateFeedbackDto = {
        userId: 1,
        recommendationType: 'v2',
        feedbackText: 'Great!',
        isPositive: true,
      };
      jest.spyOn(prisma.feedback, 'create').mockRejectedValue(new Error('DB Error'));

      await expect(service.submitFeedback(feedbackDto)).rejects.toThrow('Failed to store feedback.');
    });
  });

  describe('getFeedbackByCustomerId', () => {
    it('should return feedback for a customer', async () => {
      const customerId = 1;
      const mockFeedback = [{
        id: 1,
        userId: customerId,
        recommendationType: 'v1',
        feedbackText: 'Test',
        isPositive: true,
        createdAt: new Date(),
      }];
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue({ customer_id: customerId } as any);
      jest.spyOn(prisma.feedback, 'findMany').mockResolvedValue(mockFeedback);

      const result = await service.getFeedbackByCustomerId(customerId);
      expect(result).toBe(mockFeedback);
      expect(prisma.feedback.findMany).toHaveBeenCalledWith({ where: { userId: customerId }, orderBy: { createdAt: 'desc' } });
    });

    it('should throw NotFoundException if customer not found when getting feedback', async () => {
      const customerId = 999;
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(null);

      await expect(service.getFeedbackByCustomerId(customerId)).rejects.toThrow(NotFoundException);
    });
  });

  // Add tests for private helper methods (getTotalSpent, getRentalCount, etc.)
  // Add tests for getRecommendationsBasedOnClientRentalCategories (v1)
});
