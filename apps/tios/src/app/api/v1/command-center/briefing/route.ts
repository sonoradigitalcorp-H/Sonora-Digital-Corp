import { NextResponse } from 'next/server';
import { generateBriefing } from '@/lib/data-generator';

export async function GET() {
  return NextResponse.json(generateBriefing());
}
