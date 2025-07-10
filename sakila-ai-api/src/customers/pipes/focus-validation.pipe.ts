
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';
import { CustomersService } from '../customers.service';

@Injectable()
export class FocusValidationPipe implements PipeTransform {
  constructor(private readonly customersService: CustomersService) {}

  transform(value: any, metadata: ArgumentMetadata) {
    const validFocusOptions = this.customersService.getRecommendationFocusOptions();

    if (value && !validFocusOptions.includes(value)) {
      throw new BadRequestException(`Invalid focus option. Valid options are: ${validFocusOptions.join(', ')}`);
    }
    return value;
  }
}
