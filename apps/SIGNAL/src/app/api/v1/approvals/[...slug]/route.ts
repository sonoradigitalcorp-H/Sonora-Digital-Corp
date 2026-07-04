import { NextRequest, NextResponse } from 'next/server';
import { generateApproval } from '@/lib/data-generator';

export async function GET(
  request: NextRequest,
  context: any
) {
  const params = await context.params;
  const slug: string[] = params.slug;
  const [id] = slug;
  const action = slug[1];

  if (action === 'approve' || action === 'reject') {
    return NextResponse.json({
      success: true,
      approvalId: id,
      action: action === 'approve' ? 'approved' : 'rejected',
      message: action === 'approve'
        ? 'Deal approved. Proceeding to contract stage.'
        : 'Deal rejected. Reason logged for review.',
      timestamp: new Date().toISOString(),
    });
  }

  return NextResponse.json(generateApproval(id));
}

export async function POST(
  request: NextRequest,
  context: any
) {
  const params = await context.params;
  const slug: string[] = params.slug;
  const [id] = slug;
  const action = slug[1];
  const body = await request.json().catch(() => ({}));

  if (action === 'approve') {
    return NextResponse.json({
      success: true,
      approvalId: id,
      action: 'approved',
      message: 'Deal approved. Proceeding to contract stage.',
      timestamp: new Date().toISOString(),
    });
  }

  if (action === 'reject') {
    return NextResponse.json({
      success: true,
      approvalId: id,
      action: 'rejected',
      message: body.reason
        ? `Deal rejected. Reason: ${body.reason}`
        : 'Deal rejected. No reason provided.',
      timestamp: new Date().toISOString(),
    });
  }

  return NextResponse.json({ success: false, error: 'Invalid action' }, { status: 400 });
}
