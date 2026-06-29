import { NextResponse } from 'next/server';
import { generateSettings } from '@/lib/data-generator';

export async function GET() {
  return NextResponse.json(generateSettings());
}
