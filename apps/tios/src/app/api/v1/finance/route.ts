import { NextResponse } from 'next/server';
import { generateFinanceData } from '@/lib/data-generator';

export async function GET() {
  return NextResponse.json(generateFinanceData());
}
