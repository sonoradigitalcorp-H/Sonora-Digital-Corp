import { NextResponse } from 'next/server';
import { generatePipeline } from '@/lib/data-generator';

export async function GET() {
  return NextResponse.json(generatePipeline());
}
