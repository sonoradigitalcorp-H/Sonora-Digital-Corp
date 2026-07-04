import { NextResponse } from 'next/server';
import { generateMarketData } from '@/lib/data-generator';

export async function GET() {
  return NextResponse.json(generateMarketData());
}
