"use client";
import { useEffect, useState, useRef, useCallback } from "react";

export type RealtimeEvent = {
  channel: string;
  data: any;
  timestamp: number;
};

interface RealtimeOptions {
  wsUrl?: string;
  onEvent?: (event: RealtimeEvent) => void;
  onStatus?: (status: "connecting" | "connected" | "disconnected") => void;
}

export function useRealtime(opts: RealtimeOptions = {}) {
  const [events, setEvents] = useState<RealtimeEvent[]>([]);
  const [status, setStatus] = useState<"connecting" | "connected" | "disconnected">("disconnected");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const wsUrl = opts.wsUrl || process.env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8787/ws";
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus("connected");
      opts.onStatus?.("connected");
    };
    ws.onclose = () => {
      setStatus("disconnected");
      opts.onStatus?.("disconnected");
      wsRef.current = null;
    };

    ws.onmessage = (e) => {
      try {
        const parsed = JSON.parse(e.data);
        const event: RealtimeEvent = {
          channel: parsed.channel,
          data: parsed.data,
          timestamp: Date.now(),
        };
        setEvents((prev) => [event, ...prev].slice(0, 200));
        opts.onEvent?.(event);
      } catch {}
    };

    return () => ws.close();
  }, [opts.wsUrl, opts.onEvent, opts.onStatus]);

  const send = useCallback((type: string, payload: any) => {
    wsRef.current?.send(JSON.stringify({ type, ...payload }));
  }, []);

  const callMcp = useCallback(async (tool: string, args: any = {}) => {
    send("mcp", { tool, args });
  }, [send]);

  const clearEvents = useCallback(() => setEvents([]), []);

  return { events, status, send, callMcp, clearEvents };
}
