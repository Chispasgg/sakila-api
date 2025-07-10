import { Controller, Get, Param, ParseIntPipe, Post, Body } from '@nestjs/common';
import { CustomersService } from './customers.service';
import { CreateFeedbackDto } from './dto/create-feedback.dto';

@Controller('customers')
export class CustomersController {
  constructor(
    private readonly customersService: CustomersService,
  ) {}

  @Get(':id/dashboard')
  getDashboard(@Param('id', ParseIntPipe) id: number) {
    return this.customersService.getDashboard(id);
  }

  @Post('feedback')
  async submitFeedback(@Body() feedbackDto: CreateFeedbackDto) {
    return this.customersService.submitFeedback(feedbackDto);
  }

  @Get(':id/feedback')
  async getCustomerFeedback(@Param('id', ParseIntPipe) id: number) {
    return this.customersService.getFeedbackByCustomerId(id);
  }
}