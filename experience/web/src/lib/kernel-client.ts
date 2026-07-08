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

type StateCallback = (msg: KernelMessage) => void;
type ResultCallback = (result: KernelResponse) => void;
type ErrorCallback = (err: string) => void;

export class KernelClient {
  private ws: WebSocket | null = null;
  private url: string;
  private onStateCb: StateCallback | null = null;
  private onResultCb: ResultCallback | null = null;
  private onErrorCb: ErrorCallback | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private _connected = false;

  constructor(url = 'ws://localhost:8001/kernel/ws') {
    this.url = url;
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    try {
      this.ws = new WebSocket(this.url);
      this.ws.onopen = () => { this._connected = true; };
      this.ws.onclose = () => { this._connected = false; this.scheduleReconnect(); };
      this.ws.onerror = () => { this._connected = false; this.onErrorCb?.('WebSocket error'); };
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'orb.state') this.onStateCb?.(data as KernelMessage);
          else this.onResultCb?.(data as KernelResponse);
        } catch { this.onErrorCb?.('Invalid message'); }
      };
    } catch { this.scheduleReconnect(); }
  }

  send(input: string) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ input, channel: 'web', timestamp: new Date().toISOString() }));
  }

  onStateChange(cb: StateCallback) { this.onStateCb = cb; }
  onResult(cb: ResultCallback) { this.onResultCb = cb; }
  onError(cb: ErrorCallback) { this.onErrorCb = cb; }

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
    this._connected = false;
  }

  get isConnected() { return this._connected; }
}
