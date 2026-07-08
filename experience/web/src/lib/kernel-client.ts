// Kernel WebSocket Client (HAS-009)
// Connects to Hermes Kernel via WebSocket for real-time communication.

export type KernelMessage = {
  type: 'orb.state';
  state: string;
  message: string;
  progress: number | null;
  actions: { id: string; label: string }[];
  metadata?: Record<string, unknown>;
};

export type KernelResponse = {
  task_id: string;
  status: string;
  agent?: string;
  duration_ms?: number;
  output?: Record<string, unknown>;
};

export class KernelClient {
  private ws: WebSocket | null = null;
  private url: string;
  private onState: ((msg: KernelMessage) => void) | null = null;
  private onResult: ((result: KernelResponse) => void) | null = null;
  private onError: ((err: string) => void) | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private connected = $state(false);

  constructor(url = 'ws://localhost:8000/kernel/ws') {
    this.url = url;
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    try {
      this.ws = new WebSocket(this.url);
      this.ws.onopen = () => { this.connected = true; };
      this.ws.onclose = () => { this.connected = false; this.scheduleReconnect(); };
      this.ws.onerror = () => { this.connected = false; this.onError?.('WebSocket error'); };
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'orb.state') this.onState?.(data as KernelMessage);
          else this.onResult?.(data as KernelResponse);
        } catch { this.onError?.('Invalid message'); }
      };
    } catch { this.scheduleReconnect(); }
  }

  send(input: string) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ input, channel: 'web', timestamp: new Date().toISOString() }));
  }

  onStateChange(cb: (msg: KernelMessage) => void) { this.onState = cb; }
  onResult(cb: (result: KernelResponse) => void) { this.onResult = cb; }
  onError(cb: (err: string) => void) { this.onError = cb; }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, 3000);
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
    this.connected = false;
  }

  get isConnected() { return this.connected; }
}
