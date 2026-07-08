// Orb State Machine (HAS-009)

export type OrbState = 'idle' | 'listening' | 'thinking' | 'executing' | 'completed' | 'alert';

export interface OrbTransition {
  from: OrbState;
  to: OrbState;
  timestamp: number;
}

const ALLOWED: Record<OrbState, OrbState[]> = {
  idle: ['listening'],
  listening: ['thinking', 'idle'],
  thinking: ['executing', 'listening', 'alert'],
  executing: ['completed', 'alert', 'thinking'],
  completed: ['idle', 'listening'],
  alert: ['idle'],
};

export class OrbMachine {
  state = $state<OrbState>('idle');
  message = $state('');
  progress = $state<number | null>(null);
  actions = $state<{ id: string; label: string }[]>([]);
  history: OrbTransition[] = [];

  transition(to: OrbState, opts?: { message?: string; progress?: number | null; actions?: { id: string; label: string }[] }): boolean {
    if (!ALLOWED[this.state].includes(to)) return false;
    this.history.push({ from: this.state, to, timestamp: Date.now() });
    this.state = to;
    if (opts?.message !== undefined) this.message = opts.message;
    if (opts?.progress !== undefined) this.progress = opts.progress;
    if (opts?.actions !== undefined) this.actions = opts.actions;
    return true;
  }

  listen() { this.transition('listening', { message: 'Listening...' }); }
  think(msg?: string) { this.transition('thinking', { message: msg || 'Thinking...' }); }
  execute(msg: string, p: number) { this.transition('executing', { message: msg, progress: p }); }
  complete(msg: string) { this.transition('completed', { message: msg, progress: 100 }); }
  alert(msg: string) { this.transition('alert', { message: msg }); }
  reset() { this.transition('idle', { message: '', progress: null, actions: [] }); }
}
