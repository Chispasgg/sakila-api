import { Injectable, BadGatewayException, BadRequestException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom, timeout, retry } from 'rxjs';

@Injectable()
export class ExternalRecommendationsService {
  private readonly ML_SERVICE_BASE_URL: string;

  constructor(
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {
    this.ML_SERVICE_BASE_URL =
      this.configService.get<string>('ML_SERVICE_BASE_URL') ||
      'http://localhost:2207';
  }

  async getRecommendationsFromExternalApi(customerId: number, focus?: string): Promise<any> {
    const url = `${this.ML_SERVICE_BASE_URL}/recommendations`;
    const params: any = { user_id: customerId };
    params.focus = focus;

    try {
      const response = await firstValueFrom(
        this.httpService.get(url, {
          params,
          headers: {
            'Accept': 'application/json',
          },
        }),
      );
      return response.data;
    } catch (error) {
      // Manejo de errores: puedes loguear el error, lanzar una excepción HTTP, etc.
      throw new Error(`Failed to get recommendations from external API: ${error.message}`);
    }
  }

  async getRecommendationsFromExternalApiV2(customerId: number): Promise<any> {
    const url = `${this.ML_SERVICE_BASE_URL}/fulltext-recommendations`;
    const params: any = { user_id: customerId };

    try {
      const response = await firstValueFrom(
        this.httpService.get(url, {
          params,
          headers: {
            'Accept': 'application/json',
          },
        }),
      );
      return response.data;
    } catch (error) {
      // Manejo de errores: puedes loguear el error, lanzar una excepción HTTP, etc.
      throw new Error(`Failed to get recommendations from external API: ${error.message}`);
    }
  }
}
