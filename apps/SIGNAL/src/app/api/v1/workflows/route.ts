import { NextResponse } from 'next/server';
import { generateWorkflows } from '@/lib/data-generator';

export async function GET() {
  const workflows = generateWorkflows();
  return NextResponse.json({
    workflows,
    total: workflows.length,
    summary: {
      running: workflows.filter(w => w.status === 'running').length,
      paused: workflows.filter(w => w.status === 'paused').length,
      waiting_approval: workflows.filter(w => w.status === 'waiting_approval').length,
      completed: workflows.filter(w => w.status === 'completed').length,
      failed: workflows.filter(w => w.status === 'failed').length,
    },
    updatedAt: new Date().toISOString(),
  });
}
