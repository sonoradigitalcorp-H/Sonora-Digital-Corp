import { NextRequest, NextResponse } from 'next/server';
import { generateWorkflows, generateArtists } from '@/lib/data-generator';

export async function GET(
  request: NextRequest,
  context: any
) {
  const params = await context.params;
  const slug: string[] = params.slug;
  const [id] = slug;
  const allWorkflows = generateWorkflows();
  const workflow = allWorkflows.find(w => w.id === id) || allWorkflows[0];

  if (slug[1] === 'approvals') {
    return NextResponse.json({
      approvals: workflow.steps
        .filter(s => s.status === 'in_progress')
        .map(s => ({
          id: `app-${id}-${workflow.steps.indexOf(s)}`,
          stepName: s.name,
          status: 'pending',
          assignedAgent: s.agent,
          message: `Aprobación requerida para: ${s.name}`,
          createdAt: new Date().toISOString(),
        })),
    });
  }

  return NextResponse.json(workflow);
}
