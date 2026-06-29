'use client';

import { useState } from 'react';
import useSWR, { mutate } from 'swr';
import { AlertTriangle, CheckCircle, XCircle, Loader2, MessageSquare } from 'lucide-react';

type ApprovalRequest = {
  id: string;
  stepName: string;
  status: string;
  assignedAgent: string;
  message: string;
  createdAt: string;
};

const fetcher = (url: string) => fetch(url).then(r => r.json());

export function ApprovalGate({ workflowId }: { workflowId: string }) {
  const [processing, setProcessing] = useState<string | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [activeModal, setActiveModal] = useState<{ id: string; action: 'approve' | 'reject' } | null>(null);

  const { data, error, isLoading } = useSWR<{ approvals: ApprovalRequest[] }>(
    `/api/v1/workflows/${workflowId}/approvals`,
    fetcher,
  );

  const submit = async (id: string, action: 'approve' | 'reject') => {
    if (action === 'reject' && !rejectionReason.trim()) return;
    setProcessing(id);
    try {
      const res = await fetch(`/api/v1/approvals/${id}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: action === 'reject' ? JSON.stringify({ reason: rejectionReason }) : undefined,
      });
      if (!res.ok) throw new Error('Request failed');
      await mutate(`/api/v1/workflows/${workflowId}/approvals`);
      setActiveModal(null);
      setRejectionReason('');
    } catch {
      // handled silently
    } finally {
      setProcessing(null);
    }
  };

  if (error) return null;
  if (isLoading) return null;
  if (!data?.approvals?.length) return null;

  return (
    <div className="rounded-xl border bg-card p-6 space-y-4">
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-5 w-5 text-amber-500" />
        <h3 className="font-semibold">Pending Approvals</h3>
        <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-500 font-medium">
          {data.approvals.length}
        </span>
      </div>

      <div className="space-y-3">
        {data.approvals.map(req => (
          <div key={req.id} className="rounded-lg border p-4 space-y-3">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <p className="font-medium text-sm">{req.message}</p>
                <p className="text-xs text-muted-foreground">Step: {req.stepName}</p>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <MessageSquare className="h-3 w-3" />
                    {req.assignedAgent}
                  </span>
                  <span className="flex items-center gap-1">{req.createdAt ? new Date(req.createdAt).toLocaleDateString() : ''}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveModal({ id: req.id, action: 'approve' })}
                disabled={processing === req.id}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-green-500/10 text-green-500 text-xs font-medium hover:bg-green-500/20 transition-colors disabled:opacity-50"
              >
                {processing === req.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <CheckCircle className="h-3 w-3" />}
                Approve
              </button>
              <button
                onClick={() => setActiveModal({ id: req.id, action: 'reject' })}
                disabled={processing === req.id}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/10 text-red-500 text-xs font-medium hover:bg-red-500/20 transition-colors disabled:opacity-50"
              >
                {processing === req.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <XCircle className="h-3 w-3" />}
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Approve / Reject Modal */}
      {activeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => { setActiveModal(null); setRejectionReason(''); }}>
          <div className="rounded-xl border bg-card p-6 max-w-sm w-full mx-4 shadow-2xl" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-semibold mb-2 capitalize">{activeModal.action} Approval</h3>
            <p className="text-sm text-muted-foreground mb-4">
              {activeModal.action === 'approve' ? 'Confirm approval of this request?' : 'Provide a reason for rejection.'}
            </p>

            {activeModal.action === 'reject' && (
              <textarea
                value={rejectionReason}
                onChange={e => setRejectionReason(e.target.value)}
                placeholder="Reason for rejection (required)"
                rows={3}
                className="w-full rounded-lg border bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 mb-4"
              />
            )}

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => { setActiveModal(null); setRejectionReason(''); }}
                className="px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => submit(activeModal.id, activeModal.action)}
                disabled={activeModal.action === 'reject' && !rejectionReason.trim()}
                className={`px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50 ${
                  activeModal.action === 'reject' ? 'bg-destructive hover:bg-destructive/90' : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {activeModal.action === 'approve' ? 'Approve' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


