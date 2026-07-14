"use client";
import { useState, useCallback } from "react";
import type { MemoryEntry } from "./types";

interface MemoryOptions {
  tenant: string;
  userId?: string;
}

export function useMemory(opts: MemoryOptions) {
  const [loading, setLoading] = useState(false);

  const save = useCallback(async (key: string, value: string, tags = "") => {
    setLoading(true);
    try {
      const resp = await fetch("/api/mcp/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "engram_save",
          args: { tenant_id: opts.tenant, key, value, user_id: opts.userId || "", tags },
        }),
      });
      const data = await resp.json();
      return data?.result?.saved === true;
    } catch { return false; }
    finally { setLoading(false); }
  }, [opts.tenant, opts.userId]);

  const get = useCallback(async (key: string): Promise<MemoryEntry | null> => {
    try {
      const resp = await fetch("/api/mcp/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "engram_get",
          args: { tenant_id: opts.tenant, key, user_id: opts.userId || "" },
        }),
      });
      const data = await resp.json();
      return data?.result?.found ? data.result : null;
    } catch { return null; }
  }, [opts.tenant, opts.userId]);

  const search = useCallback(async (query: string, limit = 10): Promise<MemoryEntry[]> => {
    try {
      const resp = await fetch("/api/mcp/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "engram_search",
          args: { tenant_id: opts.tenant, query, user_id: opts.userId || "", limit },
        }),
      });
      const data = await resp.json();
      return data?.result?.results || [];
    } catch { return []; }
  }, [opts.tenant, opts.userId]);

  return { save, get, search, loading };
}
