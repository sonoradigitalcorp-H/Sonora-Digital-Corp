'use client';

import { useState } from 'react';
import useSWR, { mutate } from 'swr';
import { Pause, Play, XCircle, RotateCcw, Loader2 } from 'lucide-react';

type Props = {
  workflowId: string;
  status: string;
};

export function WorkflowControls({ workflowId, status }: Props) {
  const [loading, setLoading] = useState<string | null>(null);
  const [confirmAction, setConfirmAction] = useState<string | null>(null);

  const callAction = async (action: string) => {
    setLoading(action);
    setConfirmAction(null);
    try {
      const res = await fetch(`/api/v1/workflows/${workflowId}/${action}`, { method: 'POST' });
      if (!res.ok) throw new Error('Request failed');
      await mutate(`/api/v1/workflows/${workflowId}`);
    } catch {
      // error handled silently
    } finally {
      setLoading(null);
    }
  };

  const isRunning = status === 'running';
  const isPaused = status === 'paused';
  const isFailed = status === 'failed';
  const isCompleted = status === 'completed';
  const isTerminal = isCompleted;

  return (
    <>
      <div className="flex items-center gap-3">
        {/* Pause / Resume */}
        {!isTerminal && !isFailed && (
          <button
            onClick={() => isRunning ? setConfirmAction('pause') : setConfirmAction('resume')}
            disabled={loading !== null}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-50"
          >
            {loading === 'pause' || loading === 'resume' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : isRunning ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            {isRunning ? 'Pause' : 'Resume'}
          </button>
        )}

        {/* Retry — only for failed */}
        {isFailed && (
          <button
            onClick={() => setConfirmAction('retry')}
            disabled={loading !== null}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-amber-500/30 bg-amber-500/10 text-amber-500 text-sm hover:bg-amber-500/20 transition-colors disabled:opacity-50"
          >
            {loading === 'retry' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RotateCcw className="h-4 w-4" />
            )}
            Retry
          </button>
        )}

        {/* Cancel */}
        {!isTerminal && (
          <button
            onClick={() => setConfirmAction('cancel')}
            disabled={loading !== null}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-red-500/30 bg-red-500/10 text-red-500 text-sm hover:bg-red-500/20 transition-colors disabled:opacity-50"
          >
            {loading === 'cancel' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <XCircle className="h-4 w-4" />
            )}
            Cancel
          </button>
        )}
      </div>

      {/* Confirmation Dialog */}
      {confirmAction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setConfirmAction(null)}>
          <div className="rounded-xl border bg-card p-6 max-w-sm w-full mx-4 shadow-2xl" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-semibold mb-2">Confirm {confirmAction}</h3>
            <p className="text-sm text-muted-foreground mb-6">
              Are you sure you want to {confirmAction} this workflow?
            </p>
            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setConfirmAction(null)}
                className="px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => callAction(confirmAction)}
                className={`px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors ${
                  confirmAction === 'cancel' ? 'bg-destructive hover:bg-destructive/90' : 'bg-primary hover:opacity-90'
                }`}
              >
                {confirmAction === 'cancel' ? 'Yes, Cancel' : `Yes, ${confirmAction.charAt(0).toUpperCase() + confirmAction.slice(1)}`}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
