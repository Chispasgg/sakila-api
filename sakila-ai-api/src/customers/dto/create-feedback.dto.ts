import { IsBoolean, IsInt, IsNotEmpty, IsOptional, IsString } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateFeedbackDto {
  @ApiProperty({ description: 'ID del usuario que proporciona el feedback.', example: 1 })
  @IsInt()
  @IsNotEmpty()
  userId: number;

  @ApiProperty({ description: 'Tipo de recomendación a la que se refiere el feedback (ej. v1, external).', example: 'v1' })
  @IsString()
  @IsNotEmpty()
  recommendationType: string;

  @ApiProperty({ description: 'Texto libre del feedback del usuario.', required: false, example: 'Me gustaron mucho las recomendaciones de acción.' })
  @IsString()
  @IsOptional()
  feedbackText?: string;

  @ApiProperty({ description: 'Indica si el feedback es positivo (true) o negativo (false).', example: true })
  @IsBoolean()
  @IsNotEmpty()
  isPositive: boolean;
}
