import { NextResponse } from 'next/server';
import { generateAgents } from '@/lib/data-generator';

export async function GET() {
  return NextResponse.json(generateAgents());
}
