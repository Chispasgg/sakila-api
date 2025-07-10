import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

@Injectable()
export class FocusValidationV2Pipe implements PipeTransform<string | undefined, string> {
  readonly allowedFocusOptions = ['categories', 'actors', 'languages', 'ratings', 'directors', 'popularity'];
  readonly defaultFocusOption = 'actors'; // Define a default valid focus

  transform(value: string | undefined, metadata: ArgumentMetadata): string {
    if (value === undefined || value === null || value === '') {
      return this.defaultFocusOption; // Return default valid focus if not provided
    }

    const focus = value.toLowerCase();

    if (!this.isValidFocus(focus)) {
      throw new BadRequestException(`Invalid focus option: ${value}. Allowed options are: ${this.allowedFocusOptions.join(', ')}`);
    }
    return focus;
  }

  private isValidFocus(focus: any): boolean {
    return this.allowedFocusOptions.includes(focus);
  }
}