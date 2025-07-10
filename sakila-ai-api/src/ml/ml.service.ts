import {
  Injectable,
  NotFoundException,
  Logger,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';
import axios from 'axios';

@Injectable()
export class MlService {
  private readonly logger = new Logger(MlService.name);
  private readonly ML_SERVICE_BASE_URL: string;

  constructor(
    private readonly prisma: PrismaService,
    private readonly configService: ConfigService,
  ) {
    this.ML_SERVICE_BASE_URL =
      this.configService.get<string>('ML_SERVICE_BASE_URL') ||
      'http://localhost:2207';
  }

  async getRecommendations(customerId: number): Promise<any> {
    this.logger.log(`Getting ML recommendations for customer ${customerId}`);

    // Verificar que el cliente exista en nuestra base de datos local
    const customer = await this.prisma.customer.findUnique({
      where: { customer_id: customerId },
    });

    if (!customer) {
      throw new NotFoundException(`Customer with ID ${customerId} not found`);
    }

    try {
      // Hacer llamada HTTP al servicio ML externo
      const response = await axios.get(
        `${this.ML_SERVICE_BASE_URL}/ml/recommendations/${customerId}`,
        {
          headers: {
            accept: 'application/json',
          },
          timeout: 10000, // 10 segundos timeout
        },
      );

      this.logger.log(
        `Successfully received ML recommendations for customer ${customerId}`,
      );
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(
        `Error calling ML service for customer ${customerId}:`,
        errorMessage,
      );

      return this.handleHttpError(error, customerId);
    }
  }

  private handleHttpError(error: unknown, customerId: number): never {
    if (error && typeof error === 'object') {
      const axiosError = error as Record<string, any>;

      if (
        axiosError.code === 'ECONNREFUSED' ||
        axiosError.code === 'ENOTFOUND'
      ) {
        throw new HttpException(
          'ML recommendation service is currently unavailable',
          HttpStatus.SERVICE_UNAVAILABLE,
        );
      }

      const response = axiosError.response as Record<string, any> | undefined;
      const status = response?.status as number;
      if (status === 404) {
        throw new NotFoundException(
          `No recommendations found for customer ${customerId}`,
        );
      }

      if (status && typeof status === 'number') {
        throw new HttpException('ML service error', status);
      }
    }

    // Error genérico
    throw new HttpException(
      'Failed to get ML recommendations',
      HttpStatus.INTERNAL_SERVER_ERROR,
    );
  }
}
