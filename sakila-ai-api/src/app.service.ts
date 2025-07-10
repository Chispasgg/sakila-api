import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHello(): { status: boolean; date: string } {
    return {
      status: true,
      date: new Date().toISOString(),
    };
  }
}
