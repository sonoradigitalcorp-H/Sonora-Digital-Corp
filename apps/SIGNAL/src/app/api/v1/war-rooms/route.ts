import { NextRequest, NextResponse } from 'next/server';
import { generateWarRooms } from '@/lib/data-generator';

export async function GET() {
  const warRooms = generateWarRooms();
  return NextResponse.json({
    warRooms,
    total: warRooms.length,
    totalValue: warRooms.reduce((a, w) => a + w.deal, 0),
    stages: [
      { label: 'Discovery', count: warRooms.filter(w => w.stage === 'discovery').length },
      { label: 'Initial Contact', count: warRooms.filter(w => w.stage === 'initial_contact').length },
      { label: 'Due Diligence', count: warRooms.filter(w => w.stage === 'due_diligence').length },
      { label: 'Negotiation', count: warRooms.filter(w => w.stage === 'negotiation').length },
    ],
    updatedAt: new Date().toISOString(),
  });
}
