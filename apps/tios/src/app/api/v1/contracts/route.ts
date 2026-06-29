import { NextRequest, NextResponse } from 'next/server';
import { generateContracts } from '@/lib/data-generator';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const status = searchParams.get('status');
  const type = searchParams.get('type');

  let contracts = generateContracts();

  if (status && status !== 'all') {
    contracts = contracts.filter(c => c.status === status);
  }
  if (type && type !== 'all') {
    contracts = contracts.filter(c => c.type.toLowerCase() === type.toLowerCase());
  }

  return NextResponse.json({
    contracts,
    total: contracts.length,
    stats: {
      pending_review: contracts.filter(c => c.status === 'pending_review').length,
      draft: contracts.filter(c => c.status === 'draft').length,
      negotiation: contracts.filter(c => c.status === 'negotiation').length,
      signed: contracts.filter(c => c.status === 'signed').length,
      terminated: contracts.filter(c => c.status === 'terminated').length,
    },
    updatedAt: new Date().toISOString(),
  });
}
