import { Test, TestingModule } from '@nestjs/testing';
import { CustomersController } from './customers.controller';
import { CustomersService } from './customers.service';
import { CreateFeedbackDto } from './dto/create-feedback.dto';

describe('CustomersController', () => {
  let controller: CustomersController;
  let service: CustomersService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [CustomersController],
      providers: [
        {
          provide: CustomersService,
          useValue: {
            getDashboard: jest.fn(),
            submitFeedback: jest.fn(),
            getFeedbackByCustomerId: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get<CustomersController>(CustomersController);
    service = module.get<CustomersService>(CustomersService);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  describe('getDashboard', () => {
    it('should return a customer dashboard', async () => {
      const customerId = 1;
      const result = {
        customer_id: customerId,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        dashboard: {
          most_rented_categories: [],
          most_rented_actors: [],
          most_rented_languages: [],
          total_spent: 100.50,
          total_rentals: 10,
          average_rating_of_films_rented: 3.5,
          last_rental_info: null,
          number_of_overdue_returns: 0,
          links: {
            recommendations_based_on_client_rental_categories: `/customers/${customerId}/recommendations_based_on_client_rental_categories`,
          },
        },
      };
      jest.spyOn(service, 'getDashboard').mockResolvedValue(result);

      expect(await controller.getDashboard(customerId)).toBe(result);
      expect(service.getDashboard).toHaveBeenCalledWith(customerId);
    });
  });

  describe('submitFeedback', () => {
    it('should submit feedback successfully', async () => {
      const feedbackDto: CreateFeedbackDto = {
        userId: 1,
        recommendationType: 'v2',
        feedbackText: 'Great!',
        isPositive: true,
      };
      const result = 'Feedback received and stored successfully!';
      jest.spyOn(service, 'submitFeedback').mockResolvedValue(result);

      expect(await controller.submitFeedback(feedbackDto)).toBe(result);
      expect(service.submitFeedback).toHaveBeenCalledWith(feedbackDto);
    });
  });

  describe('getCustomerFeedback', () => {
    it('should return customer feedback', async () => {
      const customerId = 1;
      const result = [{ id: 1, userId: customerId, feedbackText: 'Test' }];
      jest.spyOn(service, 'getFeedbackByCustomerId').mockResolvedValue(result);

      expect(await controller.getCustomerFeedback(customerId)).toBe(result);
      expect(service.getFeedbackByCustomerId).toHaveBeenCalledWith(customerId);
    });
  });
});
