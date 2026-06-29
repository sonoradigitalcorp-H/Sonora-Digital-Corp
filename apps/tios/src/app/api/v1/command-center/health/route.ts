import { NextResponse } from 'next/server';
import { generateHealthStatus } from '@/lib/data-generator';

export async function GET() {
  return NextResponse.json(generateHealthStatus());
}
