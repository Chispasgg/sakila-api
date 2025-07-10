import { Test, TestingModule } from '@nestjs/testing';
import { MlService } from './ml.service';
import { PrismaService } from '../prisma/prisma.service';
import { NotFoundException, HttpException, HttpStatus } from '@nestjs/common';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('MlService', () => {
  let service: MlService;
  let prisma: PrismaService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        MlService,
        {
          provide: PrismaService,
          useValue: {
            customer: {
              findUnique: jest.fn(),
            },
          },
        },
      ],
    }).compile();

    service = module.get<MlService>(MlService);
    prisma = module.get<PrismaService>(PrismaService);

    // Reset mocks
    jest.clearAllMocks();
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('getRecommendations', () => {
    const customerId = 4;
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

    const mockMLResponse = {
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
          recommendation_reason:
            'Hybrid: Users like you also enjoyed similar genres',
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

    it('should return ML recommendations from external service', async () => {
      // Mock customer exists
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(mockCustomer);
      
      // Mock axios response
      mockedAxios.get.mockResolvedValue({ data: mockMLResponse });

      const result = await service.getRecommendations(customerId);

      expect(result).toEqual(mockMLResponse);
      expect(prisma.customer.findUnique).toHaveBeenCalledWith({
        where: { customer_id: customerId },
      });
      expect(mockedAxios.get).toHaveBeenCalledWith(
        `http://localhost:2207/ml/recommendations/${customerId}`,
        {
          headers: {
            accept: 'application/json',
          },
          timeout: 10000,
        },
      );
    });

    it('should throw NotFoundException when customer does not exist', async () => {
      // Mock customer not found
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(null);

      await expect(service.getRecommendations(customerId)).rejects.toThrow(
        new NotFoundException(`Customer with ID ${customerId} not found`),
      );

      expect(prisma.customer.findUnique).toHaveBeenCalledWith({
        where: { customer_id: customerId },
      });
      expect(mockedAxios.get).not.toHaveBeenCalled();
    });

    it('should throw HttpException when ML service is unavailable', async () => {
      // Mock customer exists
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(mockCustomer);
      
      // Mock connection refused error
      const connectionError = new Error('Connection refused');
      (connectionError as any).code = 'ECONNREFUSED';
      mockedAxios.get.mockRejectedValue(connectionError);

      await expect(service.getRecommendations(customerId)).rejects.toThrow(
        new HttpException(
          'ML recommendation service is currently unavailable',
          HttpStatus.SERVICE_UNAVAILABLE,
        ),
      );
    });

    it('should throw NotFoundException when ML service returns 404', async () => {
      // Mock customer exists
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(mockCustomer);
      
      // Mock 404 error
      const notFoundError = new Error('Not found');
      (notFoundError as any).response = { status: 404 };
      mockedAxios.get.mockRejectedValue(notFoundError);

      await expect(service.getRecommendations(customerId)).rejects.toThrow(
        new NotFoundException(`No recommendations found for customer ${customerId}`),
      );
    });

    it('should throw HttpException for other ML service errors', async () => {
      // Mock customer exists
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(mockCustomer);
      
      // Mock 500 error
      const serverError = new Error('Internal server error');
      (serverError as any).response = { status: 500, statusText: 'Internal Server Error' };
      mockedAxios.get.mockRejectedValue(serverError);

      await expect(service.getRecommendations(customerId)).rejects.toThrow(
        new HttpException('ML service error', 500),
      );
    });

    it('should throw generic HttpException for unknown errors', async () => {
      // Mock customer exists
      jest.spyOn(prisma.customer, 'findUnique').mockResolvedValue(mockCustomer);
      
      // Mock unknown error
      const unknownError = new Error('Unknown error');
      mockedAxios.get.mockRejectedValue(unknownError);

      await expect(service.getRecommendations(customerId)).rejects.toThrow(
        new HttpException(
          'Failed to get ML recommendations',
          HttpStatus.INTERNAL_SERVER_ERROR,
        ),
      );
    });
  });
});
