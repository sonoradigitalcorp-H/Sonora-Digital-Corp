"use client";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8787/ws";

export type AgentEvent = {
  channel: string;
  data: any;
};

export type Agent = {
  name: string;
  tenant: string;
  role: string;
  tools: string[];
  status: "idle" | "running" | "error";
  last_seen: string;
};

export async function mcpCall(tool: string, args: any = {}) {
  const resp = await fetch("http://127.0.0.1:8180/mcp/execute", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool, args }),
  });
  return resp.json();
}

export function connectWS(
  onEvent: (ev: AgentEvent) => void,
  onOpen?: () => void,
  onClose?: () => void
) {
  const ws = new WebSocket(WS_URL);
  ws.onopen = () => onOpen?.();
  ws.onclose = () => onClose?.();
  ws.onmessage = (e) => {
    try {
      onEvent(JSON.parse(e.data));
    } catch {}
  };
  return ws;
}
