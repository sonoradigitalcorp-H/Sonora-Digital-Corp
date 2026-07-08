import { NextResponse } from 'next/server';
import { generateReports } from '@/lib/data-generator';

export async function GET() {
  return NextResponse.json(generateReports());
}
