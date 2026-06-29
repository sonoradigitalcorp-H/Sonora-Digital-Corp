import { NextResponse } from 'next/server';
import { generateAnalytics } from '@/lib/data-generator';

export async function GET() {
  return NextResponse.json(generateAnalytics());
}
